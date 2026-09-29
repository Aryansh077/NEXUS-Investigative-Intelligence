from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

from ..database.connection import get_db
from ..database.models import Prediction, Complaint, Location, Alert
from ..services.prediction.engine import predict_cashout_locations
from ..security.audit import log_action

router = APIRouter()

class PredictRequest(BaseModel):
    complaint_id: str
    top_k: Optional[int] = 5
    alert_threshold: Optional[float] = 65.0

@router.post("/predict")
def run_prediction(payload: PredictRequest, db: Session = Depends(get_db)):
    try:
        result = predict_cashout_locations(
            db=db,
            complaint_id=payload.complaint_id,
            top_k=payload.top_k or 5,
            alert_threshold=payload.alert_threshold or 65.0
        )
        log_action("investigator", "RUN_PREDICTION", result["case_id"], payload.complaint_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/latest")
def get_latest_predictions(limit: int = 15, db: Session = Depends(get_db)):
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    out = []
    for p in preds:
        loc = db.query(Location).filter_by(cluster_id=p.cluster_id).first()
        expl = json.loads(p.explanation_json) if p.explanation_json else {}
        out.append({
            "id": p.id,
            "complaint_id": p.complaint_id,
            "case_id": p.case_id,
            "cluster_id": p.cluster_id,
            "cluster_name": loc.cluster_name if loc else p.cluster_id,
            "city": loc.city if loc else "Unknown",
            "risk_score": p.risk_score,
            "rank": p.rank,
            "window_start": p.window_start,
            "window_end": p.window_end,
            "model_version": p.model_version,
            "explanation": expl.get("summary", ""),
            "drivers": expl.get("drivers", []),
            "created_at": p.created_at
        })
    return out

@router.get("/{complaint_id}")
def get_complaint_predictions(complaint_id: str, db: Session = Depends(get_db)):
    preds = db.query(Prediction).filter_by(complaint_id=complaint_id).order_by(Prediction.rank.asc()).all()
    if not preds:
        # Generate live on-demand if not already generated
        try:
            return predict_cashout_locations(db, complaint_id, top_k=5)
        except Exception:
            return {"complaint_id": complaint_id, "predictions": []}
            
    out = []
    for p in preds:
        loc = db.query(Location).filter_by(cluster_id=p.cluster_id).first()
        expl = json.loads(p.explanation_json) if p.explanation_json else {}
        out.append({
            "id": p.id,
            "rank": p.rank,
            "cluster_id": p.cluster_id,
            "cluster_name": loc.cluster_name if loc else p.cluster_id,
            "city": loc.city if loc else "Unknown",
            "risk_score": p.risk_score,
            "window_start": p.window_start,
            "window_end": p.window_end,
            "prediction_window": f"{p.window_start[-8:-3]}–{p.window_end[-8:-3]}",
            "explanation": expl.get("summary", ""),
            "top_drivers": expl.get("drivers", [])
        })
    return {"complaint_id": complaint_id, "predictions": out}
