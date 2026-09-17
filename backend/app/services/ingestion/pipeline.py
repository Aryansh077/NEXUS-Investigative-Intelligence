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


def _ingest_structured_records(case_id: str, records: list[dict], original_name: str):
    created = 0
    for record in records:
        data = {str(key): str(value) for key, value in record.items()}
        evidence_id = add_evidence(
            case_id,
            "structured",
            f"{original_name} record",
            json.dumps(data, sort_keys=True),
            original_name,
            data.get("timestamp") or data.get("date"),
        )
        entities = []
        if data.get("person_id") and data.get("name"):
            resolve_or_create_entity(case_id, "PERSON", data["name"])
        for key in ["caller", "receiver", "sender", "receiver_account", "owner", "person_id", "person", "vehicle_id", "registration", "location", "account"]:
            if key == "person_id" and data.get("name"):
                continue
            if data.get(key):
                entity_type = "PERSON" if key in {"caller", "receiver", "person_id", "person", "owner"} else (
                    "VEHICLE" if key in {"vehicle_id", "registration"} else (
                        "LOCATION" if key == "location" else "OTHER"
                    )
                )
                entities.append((entity_type, data[key]))
        ids = [resolve_or_create_entity(case_id, entity_type, name) for entity_type, name in entities]
        for relationship in relations_from_record(data, ids):
            from ..relationship_extraction.extractor import store_relationship

            store_relationship(
                case_id,
                relationship["source_id"],
                relationship["target_id"],
                relationship["type"],
                relationship.get("timestamp"),
                evidence_id,
                relationship.get("confidence", 0.95),
            )
            created += 1
    return created

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

    if suffix == ".json":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        records = payload if isinstance(payload, list) else payload.get("records", [])
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise ValueError("JSON upload must contain a list of records or a records list")
        return {"ok": True, "type": "json", "rows": len(records), "relationships": _ingest_structured_records(case_id, records, original_name)}

    if suffix == ".csv":
        import pandas as pd
        df = pd.read_csv(path)
        records = [{str(k): value for k, value in row.items()} for row in df.fillna("").to_dict(orient="records")]
        return {"ok": True, "type": "csv", "rows": len(records), "relationships": _ingest_structured_records(case_id, records, original_name)}

    raise ValueError("Unsupported file")
