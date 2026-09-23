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
    case_id = payload.id.strip().upper()
    title = payload.title.strip()
    if not case_id or not title:
        raise HTTPException(400, "Case number and name are required")
    conn = get_conn()
    if conn.execute("SELECT 1 FROM cases WHERE id=?", (case_id,)).fetchone():
        conn.close()
        raise HTTPException(409, "A case with this number already exists")
    conn.execute(
        "INSERT INTO cases(id,title,description,status,created_at) VALUES (?,?,?,?,?)",
        (case_id, title, payload.description.strip(), "Active", datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return {"ok": True, "case_id": case_id}
