from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone

from ..database.connection import get_db
from ..database.models import Alert, Location, Complaint
from ..security.audit import log_action

router = APIRouter()

class AlertStatusUpdate(BaseModel):
    status: str  # New, Acknowledged, Investigating, Resolved, Dismissed
    assigned_to: Optional[str] = None
    note: Optional[str] = None

@router.get("/")
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    case_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if status:
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)
    if case_id:
        query = query.filter_by(case_id=case_id)

    alerts = query.order_by(Alert.risk_score.desc(), Alert.created_at.desc()).limit(limit).all()
    out = []
    for a in alerts:
        loc = db.query(Location).filter_by(cluster_id=a.cluster_id).first()
        out.append({
            "id": a.id,
            "case_id": a.case_id,
            "complaint_id": a.complaint_id,
            "prediction_id": a.prediction_id,
            "cluster_id": a.cluster_id,
            "cluster_name": loc.cluster_name if loc else a.cluster_id,
            "city": loc.city if loc else "Unknown",
            "risk_score": a.risk_score,
            "severity": a.severity,
            "message": a.message,
            "status": a.status,
            "assigned_to": a.assigned_to,
            "created_at": a.created_at,
            "updated_at": a.updated_at
        })
    return out

@router.patch("/{alert_id}/status")
def update_alert_status(alert_id: str, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    valid_statuses = ["New", "Acknowledged", "Investigating", "Resolved", "Dismissed"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")

    alert.status = payload.status
    if payload.assigned_to:
        alert.assigned_to = payload.assigned_to
    alert.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    log_action("investigator", f"UPDATE_ALERT_{payload.status.upper()}", alert.case_id, alert_id)
    return {"ok": True, "alert_id": alert_id, "status": alert.status, "assigned_to": alert.assigned_to}
