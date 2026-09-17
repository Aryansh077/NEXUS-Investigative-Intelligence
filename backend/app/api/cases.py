from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from ..database.db import get_conn

router = APIRouter()

class CaseCreate(BaseModel):
    id: str
    title: str
    description: str = ""

@router.get("")
def list_cases():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/{case_id}")
def get_case(case_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Case not found")
    return dict(row)

@router.post("")
def create_case(payload: CaseCreate):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO cases(id,title,description,status,created_at) VALUES (?,?,?,?,?)",
        (payload.id, payload.title, payload.description, "Active", datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return {"ok": True, "case_id": payload.id}
