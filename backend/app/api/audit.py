from fastapi import APIRouter
from ..database.db import get_conn

router = APIRouter()

@router.get("/{case_id}")
def audit(case_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM audit_logs WHERE case_id=? ORDER BY timestamp DESC", (case_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
