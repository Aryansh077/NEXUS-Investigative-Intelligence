from ...database.db import get_conn
import uuid, json

def store_relationship(case_id, source, target, rel_type, timestamp, evidence_id, confidence=0.9):
    # source/target can be IDs from structured data or names from text.
    conn = get_conn()
    def resolve(value):
        row = conn.execute("SELECT id FROM entities WHERE case_id=? AND id=?", (case_id,value)).fetchone()
        if row: return value
        row = conn.execute("SELECT id FROM entities WHERE case_id=? AND name LIKE ?", (case_id,value)).fetchone()
        return row["id"] if row else None
    s, t = resolve(str(source)), resolve(str(target))
    if not s or not t:
        conn.close()
        return None
    rid = "REL-" + uuid.uuid4().hex[:8]
    conn.execute(
        """INSERT INTO relationships(id,case_id,source_id,target_id,type,confidence,timestamp,source_record,verification,metadata_json)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (rid,case_id,s,t,rel_type,float(confidence),timestamp,evidence_id,"pending",json.dumps({}))
    )
    conn.commit()
    conn.close()
    return rid

def relations_from_record(data, ids):
    # Structured rows: first two entity IDs become a relationship where possible.
    out = []
    timestamp = data.get("timestamp") or data.get("date")
    if data.get("caller") and data.get("receiver") and len(ids) >= 2:
        out.append({"source_id":ids[0],"target_id":ids[1],"type":"CALLED","timestamp":timestamp,"confidence":0.99})
    elif data.get("sender") and data.get("receiver") and len(ids) >= 2:
        out.append({"source_id":ids[0],"target_id":ids[1],"type":"TRANSFERRED","timestamp":timestamp,"confidence":0.99})
    elif data.get("owner") and data.get("vehicle_id") and len(ids) >= 2:
        out.append({"source_id":ids[0],"target_id":ids[1],"type":"OWNS","timestamp":timestamp,"confidence":0.98})
    elif data.get("person") and data.get("location") and len(ids) >= 2:
        out.append({"source_id":ids[0],"target_id":ids[1],"type":"VISITED","timestamp":timestamp,"confidence":0.95})
    return out
