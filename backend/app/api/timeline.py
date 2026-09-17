from fastapi import APIRouter
from ..database.db import get_conn

router = APIRouter()

@router.get("/{case_id}")
def timeline(case_id: str):
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.*, e.name AS source_name, e2.name AS target_name
        FROM relationships r
        JOIN entities e ON e.id=r.source_id
        JOIN entities e2 ON e2.id=r.target_id
        WHERE r.case_id=? AND r.timestamp IS NOT NULL
        ORDER BY r.timestamp
    """, (case_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
