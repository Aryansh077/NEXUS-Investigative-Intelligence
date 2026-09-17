from collections import Counter
from ...database.db import get_conn
import math, uuid
from datetime import datetime, timezone

def detect_case_anomalies(case_id):
    conn=get_conn()
    rows=conn.execute("""
        SELECT r.source_id, e.name, r.timestamp
        FROM relationships r JOIN entities e ON e.id=r.source_id
        WHERE r.case_id=? AND r.timestamp IS NOT NULL
    """,(case_id,)).fetchall()
    conn.close()
    counts=Counter(r["source_id"] for r in rows)
    if not counts:
        return []
    vals=list(counts.values())
    mean=sum(vals)/len(vals)
    sd=math.sqrt(sum((x-mean)**2 for x in vals)/len(vals)) or 1
    out=[]
    for entity_id,count in counts.items():
        z=(count-mean)/sd
        if z>=1.5:
            out.append({
                "id":"AN-"+uuid.uuid4().hex[:8],
                "case_id":case_id,
                "entity_id":entity_id,
                "score":round(z,2),
                "severity":"high" if z>=2.5 else "medium",
                "reason":f"Observed {count} recorded interactions, above the case-network baseline."
            })
    return sorted(out,key=lambda x:-x["score"])
