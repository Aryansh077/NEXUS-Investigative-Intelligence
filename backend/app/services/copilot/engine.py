import re
from ...database.db import get_conn
from ..graph.analytics import find_path, graph_metrics

def answer_question(case_id, question):
    q=question.lower().strip()
    conn=get_conn()
    entities=[dict(r) for r in conn.execute("SELECT * FROM entities WHERE case_id=?", (case_id,)).fetchall()]
    conn.close()
    names=[e["name"] for e in entities]

    # Relationship/path question
    if ("connect" in q or "path" in q or "relationship" in q) and len(names)>=2:
        mentioned=[n for n in names if n.lower() in q]
        if len(mentioned)>=2:
            result=find_path(case_id, mentioned[0], mentioned[1])
            if result:
                evidence=sorted({s["evidence_id"] for s in result["steps"] if s.get("evidence_id")})
                return {
                    "answer": f"I found an evidence-supported path: {' → '.join(result['path'])}.",
                    "type":"path",
                    "path":result["path"],
                    "steps":result["steps"],
                    "evidence_ids":evidence,
                    "grounding":"Local NEXUS graph and evidence database"
                }

    if "central" in q or "important" in q or "connector" in q or "bridge" in q:
        m=graph_metrics(case_id)
        return {
            "answer":"The graph metrics identify entities with higher structural centrality. These are network measurements, not conclusions about criminality.",
            "type":"metrics",
            "metrics":m,
            "grounding":"Local NEXUS graph"
        }

    if "anomal" in q or "unusual" in q:
        from ..anomaly.detector import detect_case_anomalies
        a=detect_case_anomalies(case_id)
        return {
            "answer":f"I found {len(a)} potentially unusual network-activity pattern(s). Review the underlying records before drawing conclusions.",
            "type":"anomalies",
            "anomalies":a,
            "grounding":"Local NEXUS relationship data"
        }

    conn=get_conn()
    rel_count=conn.execute("SELECT COUNT(*) c FROM relationships WHERE case_id=?", (case_id,)).fetchone()["c"]
    ev_count=conn.execute("SELECT COUNT(*) c FROM evidence WHERE case_id=?", (case_id,)).fetchone()["c"]
    conn.close()
    return {
        "answer":f"I can search the current case graph and evidence. This case currently contains {rel_count} relationships and {ev_count} evidence records. Try asking how two named entities are connected, what unusual patterns were found, or which entities have high network centrality.",
        "type":"help",
        "grounding":"Local NEXUS data only"
    }
