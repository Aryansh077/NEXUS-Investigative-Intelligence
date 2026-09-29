import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[3]
METRICS_PATH = ROOT_DIR / "ml" / "evaluation" / "metrics.json"

@router.get("/metrics")
def get_model_evaluation_metrics():
    """
    Returns authentic, ground-truth-calculated evaluation metrics for:
    - Logistic Regression baseline
    - Random Forest
    - LightGBM (Champion)
    Includes Precision, Recall, F1, ROC-AUC, PR-AUC, Top-1/3/5 Hit Rates, and Latency.
    """
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found. Please train models via train_models.py first."
        )
    
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
