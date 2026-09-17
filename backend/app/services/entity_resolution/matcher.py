from rapidfuzz.fuzz import ratio
from ...database.db import get_conn
import json, uuid

def resolve_or_create_entity(case_id: str, typ: str, name: str):
    name = name.strip()
    if not name:
        return None
    conn = get_conn()
    rows = conn.execute("SELECT * FROM entities WHERE case_id=? AND type=?", (case_id, typ)).fetchall()
    best = None
    best_score = 0
    for r in rows:
        score = ratio(name.lower(), r["name"].lower()) / 100
        if score > best_score:
            best, best_score = r, score
    if best and best_score >= 0.90:
        conn.close()
        return best["id"]
    eid = "ENT-" + uuid.uuid4().hex[:8]
    conn.execute(
        "INSERT INTO entities(id,case_id,type,name,metadata_json) VALUES (?,?,?,?,?)",
        (eid,case_id,typ,name,json.dumps({"resolution_confidence": round(best_score,3) if best else None}))
    )
    conn.commit()
    conn.close()
    return eid
