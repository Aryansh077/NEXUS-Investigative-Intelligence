from pathlib import Path
import csv, json, hashlib
from datetime import datetime, timezone
from ..nlp.extractor import extract_from_text
from ..entity_resolution.matcher import resolve_or_create_entity
from ..relationship_extraction.extractor import relations_from_record
from ...database.db import get_conn

def read_text(path: str):
    p = Path(path)
    if p.suffix == ".txt":
        return p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix == ".docx":
        from docx import Document
        return "\n".join(x.text for x in Document(path).paragraphs)
    if p.suffix == ".pdf":
        import fitz
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    return ""

def add_evidence(case_id, record_type, title, content, source_file, timestamp=None):
    eid = hashlib.sha1(f"{case_id}|{title}|{content}".encode()).hexdigest()[:12]
    h = hashlib.sha256(content.encode()).hexdigest()
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO evidence(id,case_id,record_type,title,content,timestamp,source_file,hash,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (eid,case_id,record_type,title,content,timestamp,source_file,h,datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return eid

def ingest_file(case_id: str, path: str, original_name: str):
    suffix = Path(path).suffix.lower()
    if suffix in {".txt",".pdf",".docx"}:
        text = read_text(path)
        evidence_id = add_evidence(case_id, "document", original_name, text, original_name)
        extracted = extract_from_text(text)
        created = 0
        for ent in extracted["entities"]:
            resolve_or_create_entity(case_id, ent["type"], ent["text"])
        for rel in extracted["relationships"]:
            if rel.get("source") and rel.get("target"):
                # Text relationships are stored as pending/source-derived evidence.
                from ..relationship_extraction.extractor import store_relationship
                store_relationship(case_id, rel["source"], rel["target"], rel["type"], rel.get("timestamp"), evidence_id, 0.75)
                created += 1
        return {"ok": True, "type": "document", "evidence_id": evidence_id, "entities": len(extracted["entities"]), "relationships": created}

    if suffix == ".csv":
        import pandas as pd
        df = pd.read_csv(path)
        created = 0
        for _, row in df.fillna("").iterrows():
            data = {str(k): str(v) for k,v in row.items()}
            evidence_id = add_evidence(case_id, "structured", f"{original_name} record", json.dumps(data), original_name, data.get("timestamp") or data.get("date"))
            ents = []
            for key in ["caller","receiver","sender","receiver_account","owner","person_id","person","vehicle_id","registration","location","account"]:
                if data.get(key):
                    typ = "PERSON" if key in {"caller","receiver","person_id","person","owner"} else ("VEHICLE" if key in {"vehicle_id","registration"} else ("LOCATION" if key=="location" else "OTHER"))
                    ents.append((typ, data[key]))
            ids = [resolve_or_create_entity(case_id, t, n) for t,n in ents]
            for rel in relations_from_record(data, ids):
                from ..relationship_extraction.extractor import store_relationship
                store_relationship(case_id, rel["source_id"], rel["target_id"], rel["type"], rel.get("timestamp"), evidence_id, rel.get("confidence",0.95))
                created += 1
        return {"ok": True, "type": "csv", "rows": len(df), "relationships": created}

    raise ValueError("Unsupported file")
