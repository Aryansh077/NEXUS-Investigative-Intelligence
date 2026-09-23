from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database.db import get_conn
from ..security.audit import log_action

router = APIRouter()

class EvidenceReview(BaseModel):
    verification: str
    username: str = "investigator"
    note: str = ""

@router.get("/{case_id}")
def list_evidence(case_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY timestamp DESC", (case_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/{case_id}/{evidence_id}")
def get_evidence(case_id: str, evidence_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM evidence WHERE case_id=? AND id=?", (case_id, evidence_id)).fetchone()
    conn.close()
    return dict(row) if row else {"error": "not found"}

@router.delete("/{case_id}/{evidence_id}")
def delete_evidence(case_id: str, evidence_id: str, username: str = "investigator"):
    conn = get_conn()
    row = conn.execute(
        "SELECT id, source_file FROM evidence WHERE case_id=? AND id=?",
        (case_id, evidence_id),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Evidence not found")
    conn.execute(
        "DELETE FROM relationships WHERE case_id=? AND source_record=?",
        (case_id, evidence_id),
    )
    conn.execute("DELETE FROM evidence WHERE case_id=? AND id=?", (case_id, evidence_id))
    conn.commit()
    conn.close()
    log_action(username, f"evidence_deleted: {row['source_file']}", case_id, evidence_id)
    return {"ok": True, "evidence_id": evidence_id}

@router.patch("/{case_id}/{evidence_id}/verify")
def verify_evidence(case_id: str, evidence_id: str, payload: EvidenceReview):
    if payload.verification not in {"pending", "verified", "rejected"}:
        return {"error": "verification must be pending, verified, or rejected"}
    conn = get_conn()
    row = conn.execute("SELECT id FROM evidence WHERE case_id=? AND id=?", (case_id, evidence_id)).fetchone()
    if not row:
        conn.close()
        return {"error": "not found"}
    conn.execute("ALTER TABLE evidence ADD COLUMN verification TEXT DEFAULT 'pending'") if not any(
        column[1] == "verification" for column in conn.execute("PRAGMA table_info(evidence)").fetchall()
    ) else None
    conn.execute("UPDATE evidence SET verification=? WHERE case_id=? AND id=?", (payload.verification, case_id, evidence_id))
    conn.commit()
    conn.close()
    log_action(payload.username, f"evidence_{payload.verification}: {payload.note}".strip(), case_id, evidence_id)
    return {"ok": True, "evidence_id": evidence_id, "verification": payload.verification,
            "verified_at": datetime.now(timezone.utc).isoformat()}
