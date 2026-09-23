from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.anomaly.detector import detect_case_anomalies
from ..database.db import get_conn, init_db
from ..security.audit import log_action

router = APIRouter()

class AnomalyReview(BaseModel):
    verification: str
    username: str = "investigator"
    note: str = ""

@router.get("/{case_id}")
def anomalies(case_id: str):
    return detect_case_anomalies(case_id)


@router.post("/{case_id}/run")
def run_anomalies(case_id: str):
    results = detect_case_anomalies(case_id)
    init_db()
    conn = get_conn()
    for result in results:
        conn.execute("""INSERT OR REPLACE INTO anomalies
            (id, case_id, entity_id, score, severity, reason, created_at, verification)
            VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT verification FROM anomalies WHERE id=?), 'pending'))""",
            (result["id"], case_id, result["entity_id"], result["score"], result["severity"],
             result["reason"], datetime.now(timezone.utc).isoformat(), result["id"]))
    conn.commit()
    conn.close()
    return {
        "case_id": case_id,
        "model": "IsolationForest",
        "results": results,
    }

@router.patch("/{case_id}/{anomaly_id}/review")
def review_anomaly(case_id: str, anomaly_id: str, payload: AnomalyReview):
    if payload.verification not in {"pending", "investigate", "resolved", "dismissed", "escalated"}:
        return {"error": "unsupported review status"}
    init_db()
    conn = get_conn()
    cursor = conn.execute("""UPDATE anomalies SET verification=?, reviewed_by=?, reviewed_at=?, review_note=?
        WHERE case_id=? AND id=?""", (payload.verification, payload.username,
        datetime.now(timezone.utc).isoformat(), payload.note, case_id, anomaly_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return {"error": "not found"}
    log_action(payload.username, f"anomaly_{payload.verification}: {payload.note}".strip(), case_id, anomaly_id)
    return {"ok": True, "anomaly_id": anomaly_id, "verification": payload.verification}
