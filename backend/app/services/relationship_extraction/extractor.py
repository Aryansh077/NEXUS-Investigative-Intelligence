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

def relations_from_record(data, entity_ids):
    # Only create relationships whose two semantic fields are explicit in the record.
    out = []
    timestamp = data.get("timestamp") or data.get("date")

    def add(source_key, target_key, rel_type, confidence):
        source_id = entity_ids.get(source_key)
        target_id = entity_ids.get(target_key)
        if data.get(source_key) and data.get(target_key) and source_id and target_id and source_id != target_id:
            out.append({"source_id":source_id,"target_id":target_id,"type":rel_type,"timestamp":timestamp,"confidence":confidence})

    add("caller", "receiver", "CALLED", 0.99)
    add("sender", "receiver", "TRANSFERRED", 0.99)
    add("sender", "receiver_account", "TRANSFERRED", 0.99)
    add("owner", "vehicle_id", "OWNS", 0.98)
    add("owner", "registration", "OWNS", 0.98)
    add("owner", "vehicle", "OWNS", 0.98)
    add("person_id", "vehicle", "OWNS", 0.98)
    add("person", "vehicle", "OWNS", 0.98)
    add("name", "vehicle", "OWNS", 0.98)
    add("person", "location", "VISITED", 0.95)
    add("person_id", "location", "VISITED", 0.95)
    add("vehicle_id", "location", "LOCATED_AT", 0.95)
    add("registration", "location", "LOCATED_AT", 0.95)
    add("vehicle", "location", "LOCATED_AT", 0.95)
    add("person_id", "phone", "USES_PHONE", 0.98)
    add("person", "phone", "USES_PHONE", 0.98)
    add("name", "phone", "USES_PHONE", 0.98)
    add("owner", "phone", "USES_PHONE", 0.98)
    add("person_id", "account", "OWNS_ACCOUNT", 0.98)
    add("person", "account", "OWNS_ACCOUNT", 0.98)
    add("name", "account", "OWNS_ACCOUNT", 0.98)
    add("owner", "account", "OWNS_ACCOUNT", 0.98)
    return out
