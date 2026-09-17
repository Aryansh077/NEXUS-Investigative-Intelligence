from __future__ import annotations

from collections.abc import Mapping

import pandas as pd
from sklearn.ensemble import IsolationForest

from .feature_engineering import FEATURE_COLUMNS, build_entity_features


def fit_isolation_forest(
    features: pd.DataFrame, random_state: int = 42
) -> tuple[IsolationForest, pd.Series, pd.Series]:
    if features.empty:
        raise ValueError("At least one entity is required")
    model = IsolationForest(
        n_estimators=100, contamination="auto", random_state=random_state
    )
    model.fit(features[FEATURE_COLUMNS])
    predictions = pd.Series(model.predict(features[FEATURE_COLUMNS]), index=features.index)
    scores = pd.Series(model.decision_function(features[FEATURE_COLUMNS]), index=features.index)
    return model, predictions, scores


def explain_anomaly(row: pd.Series, baseline: pd.Series) -> list[str]:
    labels = {
        "interaction_count": "unusually high communication volume",
        "unique_contacts": "unusually high number of unique contacts",
        "night_interaction_count": "unusual late-night activity",
    }
    reasons = [
        label
        for feature, label in labels.items()
        if row[feature] > baseline[feature] * 1.5
        and row[feature] > baseline[feature] + 1
    ]
    return reasons or ["feature combination differs from the case baseline"]


def detect_anomalies(
    entity_ids: list[str], relationships: list[Mapping[str, object]]
) -> list[dict[str, object]]:
    features = build_entity_features(entity_ids, relationships)
    if len(features) < 2:
        return []
    _, predictions, scores = fit_isolation_forest(features)
    baseline = features.median(numeric_only=True)
    results = []
    for entity_id in features.index[predictions == -1]:
        score = max(0.0, min(1.0, 0.5 - float(scores[entity_id])))
        results.append(
            {
                "entity_id": entity_id,
                "score": round(score, 3),
                "severity": "high" if score >= 0.65 else "medium",
                "reasons": explain_anomaly(features.loc[entity_id], baseline),
                "features": {
                    column: float(features.loc[entity_id, column])
                    for column in FEATURE_COLUMNS
                },
            }
        )
    return sorted(results, key=lambda item: float(item["score"]), reverse=True)