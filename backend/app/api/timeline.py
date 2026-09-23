from fastapi import APIRouter
from ..database.db import get_conn

router = APIRouter()

@router.get("/{case_id}")
def timeline(case_id: str, entity_id: str | None = None, event_type: str | None = None,
             start: str | None = None, end: str | None = None):
    filters = ["r.case_id=?", "r.timestamp IS NOT NULL"]
    params: list[str] = [case_id]
    if entity_id:
        filters.append("(r.source_id=? OR r.target_id=?)")
        params.extend([entity_id, entity_id])
    if event_type:
        filters.append("r.type=?")
        params.append(event_type)
    if start:
        filters.append("r.timestamp >= ?")
        params.append(start)
    if end:
        filters.append("r.timestamp <= ?")
        params.append(end)
    conn = get_conn()
    rows = conn.execute(f"""
        SELECT r.*, e.name AS source_name, e2.name AS target_name
        FROM relationships r
        JOIN entities e ON e.id=r.source_id
        JOIN entities e2 ON e2.id=r.target_id
        WHERE {' AND '.join(filters)}
        ORDER BY r.timestamp
    """, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
