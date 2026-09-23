from ...database.db import get_conn
from .model import detect_anomalies

def detect_case_anomalies(case_id):
    conn=get_conn()
    entities=conn.execute("SELECT id FROM entities WHERE case_id=?", (case_id,)).fetchall()
    rows=conn.execute("""
        SELECT source_id, target_id, timestamp, confidence, source_record
        FROM relationships WHERE case_id=?
    """,(case_id,)).fetchall()
    conn.close()
    results = detect_anomalies([row["id"] for row in entities], [dict(row) for row in rows])
    return [
        {
            "id": f"AN-{index:04d}",
            "case_id": case_id,
            "entity_id": result["entity_id"],
            "score": result["score"],
            "severity": result["severity"],
            "reason": "; ".join(result["reasons"]),
            "reasons": result["reasons"],
            "features": result["features"],
            "model": "IsolationForest",
            "verification": "pending",
            "evidence_id": next((row["source_record"] for row in rows
                                  if row["source_record"] and result["entity_id"] in {row["source_id"], row["target_id"]}), None),
        }
        for index, result in enumerate(results, start=1)
    ]
