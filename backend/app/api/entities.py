from fastapi import APIRouter, HTTPException
from ..database.db import get_conn

router = APIRouter()

@router.get("/{case_id}")
def list_entities(case_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM entities WHERE case_id=? ORDER BY type,name", (case_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
