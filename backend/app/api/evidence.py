from fastapi import APIRouter
from ..database.db import get_conn

router = APIRouter()

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
