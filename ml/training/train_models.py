#!/usr/bin/env python3
"""
NEXUS-PREDICT: ML Model Training & Evaluation Engine
Trains Logistic Regression, Random Forest, and LightGBM models on synthetic cybercrime
cash-out data. Evaluates Top-K Hit Rate, PR-AUC, ROC-AUC, and Latency.
Saves trained models, evaluation metrics, and SHAP explainer artifacts.
"""

import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, brier_score_loss
)
import lightgbm as lgb
import shap

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "synthetic"
MODELS_DIR = ROOT_DIR / "ml" / "models"
EVAL_DIR = ROOT_DIR / "ml" / "evaluation"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(ROOT_DIR))
from ml.features.feature_pipeline import extract_pair_features, FEATURE_NAMES

def load_data():
    complaints = pd.read_csv(DATA_DIR / "complaints.csv").to_dict(orient="records")
    locations = pd.read_csv(DATA_DIR / "locations.csv").to_dict(orient="records")
    atms = pd.read_csv(DATA_DIR / "atms.csv")
    cases = {c["case_id"]: c for c in pd.read_csv(DATA_DIR / "cases.csv").to_dict(orient="records")}
    
    with open(DATA_DIR / "ground_truth.json", "r", encoding="utf-8") as f:
        ground_truth = {gt["complaint_id"]: gt for gt in json.load(f)}

    # Count ATMs per cluster
    atm_counts = atms.groupby("cluster_id").size().to_dict()

    # Historical cluster frequency from ground truth
    hist_counts = {}
    for gt in ground_truth.values():
        c_id = gt["actual_cluster_id"]
        hist_counts[c_id] = hist_counts.get(c_id, 0) + 1

    return complaints, locations, cases, ground_truth, atm_counts, hist_counts

def build_dataset():
    complaints, locations, cases, ground_truth, atm_counts, hist_counts = load_data()
    
    rows = []
    groups = []  # complaint_id for group ranking / evaluation
    targets = []

    for comp in complaints:
        cid = comp["complaint_id"]
        if cid not in ground_truth:
            continue
        actual_cluster = ground_truth[cid]["actual_cluster_id"]
        case = cases.get(comp["case_id"], {})

        for loc in locations:
            feats = extract_pair_features(
                complaint=comp,
                candidate_cluster=loc,
                case_context=case,
                atms_in_cluster=atm_counts.get(loc["cluster_id"], 4),
                historical_cluster_counts=hist_counts
            )
            is_match = 1 if loc["cluster_id"] == actual_cluster else 0
            feats["target"] = is_match
            feats["complaint_id"] = cid
            feats["cluster_id"] = loc["cluster_id"]
            rows.append(feats)

    df = pd.DataFrame(rows)
    return df

def evaluate_ranking(model, df_eval, feature_cols):
    """
    Evaluates Top-1, Top-3, and Top-5 Hit Rate across complaints.
    """
    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    total_queries = 0

    for cid, group in df_eval.groupby("complaint_id"):
        total_queries += 1
        X_group = group[feature_cols].values
        # Predict probability of cash-out (class 1)
        probs = model.predict_proba(X_group)[:, 1]
        ranked_indices = np.argsort(-probs)
        actual_matches = np.where(group["target"].values == 1)[0]
        if len(actual_matches) == 0:
            continue
        true_idx = actual_matches[0]

        top_1 = ranked_indices[:1]
        top_3 = ranked_indices[:3]
        top_5 = ranked_indices[:5]

        if true_idx in top_1:
            top1_hits += 1
        if true_idx in top_3:
            top3_hits += 1
        if true_idx in top_5:
            top5_hits += 1

    return {
        "top1_hit_rate": round(top1_hits / total_queries, 4) if total_queries else 0.0,
        "top3_hit_rate": round(top3_hits / total_queries, 4) if total_queries else 0.0,
        "top5_hit_rate": round(top5_hits / total_queries, 4) if total_queries else 0.0,
        "evaluated_cases": total_queries
    }

def main():
    print("=" * 60)
    print("NEXUS-PREDICT: Training Spatio-Temporal Prediction Models...")
    print("=" * 60)

    df = build_dataset()
    feature_cols = [c for c in FEATURE_NAMES if c in df.columns]
    X = df[feature_cols]
    y = df["target"]

    # Stratified or group-aware split
    unique_cids = df["complaint_id"].unique()
    train_cids, test_cids = train_test_split(unique_cids, test_size=0.25, random_state=42)

    df_train = df[df["complaint_id"].isin(train_cids)]
    df_test = df[df["complaint_id"].isin(test_cids)]

    X_train, y_train = df_train[feature_cols], df_train["target"]
    X_test, y_test = df_test[feature_cols], df_test["target"]

    print(f"Dataset: {len(df)} candidate pairs ({len(train_cids)} train complaints, {len(test_cids)} test complaints)")

    # 1. Model 1: Logistic Regression Baseline
    print("\n--- Training Model 1: Logistic Regression Baseline ---")
    start = time.time()
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr.fit(X_train, y_train)
    lr_train_time = round(time.time() - start, 4)
    lr_probs = lr.predict_proba(X_test)[:, 1]
    lr_preds = (lr_probs >= 0.5).astype(int)

    # 2. Model 2: Random Forest Classifier
    print("--- Training Model 2: Random Forest Classifier ---")
    start = time.time()
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42)
    rf.fit(X_train, y_train)
    rf_train_time = round(time.time() - start, 4)
    rf_probs = rf.predict_proba(X_test)[:, 1]
    rf_preds = (rf_probs >= 0.5).astype(int)

    # 3. Model 3: LightGBM Classifier (Primary Champion Model)
    print("--- Training Model 3: LightGBM Classifier (Champion) ---")
    start = time.time()
    scale_pos = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    lgbm = lgb.LGBMClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        scale_pos_weight=scale_pos,
        random_state=42,
        verbose=-1
    )
    lgbm.fit(X_train, y_train)
    lgbm_train_time = round(time.time() - start, 4)
    lgbm_probs = lgbm.predict_proba(X_test)[:, 1]
    lgbm_preds = (lgbm_probs >= 0.5).astype(int)

    # Measure real inference latency per sample (100 runs)
    sample_vec = X_test.iloc[:1].values
    lat_start = time.time()
    for _ in range(100):
        lgbm.predict_proba(sample_vec)
    avg_latency_ms = round(((time.time() - lat_start) / 100) * 1000, 3)

    # Calculate actual metrics
    models_comparison = {
        "LogisticRegression": {
            "precision": round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, lr_preds, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, lr_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, lr_probs)), 4),
            "pr_auc": round(float(average_precision_score(y_test, lr_probs)), 4),
            "brier_score": round(float(brier_score_loss(y_test, lr_probs)), 4),
            **evaluate_ranking(lr, df_test, feature_cols)
        },
        "RandomForest": {
            "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
            "pr_auc": round(float(average_precision_score(y_test, rf_probs)), 4),
            "brier_score": round(float(brier_score_loss(y_test, rf_probs)), 4),
            **evaluate_ranking(rf, df_test, feature_cols)
        },
        "LightGBM": {
            "precision": round(float(precision_score(y_test, lgbm_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, lgbm_preds, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, lgbm_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, lgbm_probs)), 4),
            "pr_auc": round(float(average_precision_score(y_test, lgbm_probs)), 4),
            "brier_score": round(float(brier_score_loss(y_test, lgbm_probs)), 4),
            "avg_inference_latency_ms": avg_latency_ms,
            **evaluate_ranking(lgbm, df_test, feature_cols)
        }
    }

    print("\n--- Model Evaluation Results (Unbiased, Ground-Truth Calculated) ---")
    print(json.dumps(models_comparison, indent=2))

    # Save Models
    joblib.dump(lgbm, MODELS_DIR / "champion_lightgbm.joblib")
    joblib.dump(rf, MODELS_DIR / "random_forest_baseline.joblib")
    joblib.dump(lr, MODELS_DIR / "logistic_baseline.joblib")
    
    with open(MODELS_DIR / "feature_names.json", "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)

    with open(EVAL_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "models": models_comparison,
            "best_model": "LightGBM",
            "features_used": feature_cols
        }, f, indent=2)

    # Initialize and save SHAP Explainer
    print("\n--- Initializing TreeSHAP Explainer ---")
    explainer = shap.TreeExplainer(lgbm)
    joblib.dump(explainer, MODELS_DIR / "shap_explainer.joblib")
    print("  [+] SHAP TreeExplainer persisted for explainable AI.")

    print("\n" + "=" * 60)
    print("Model training and evaluation successfully completed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
