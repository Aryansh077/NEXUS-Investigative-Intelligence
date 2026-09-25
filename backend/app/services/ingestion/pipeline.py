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


def _infer_entity_type(key: str, val: str) -> str:
    k = key.lower().strip()
    v = str(val).strip()
    if k in {"phone", "mobile", "phone_number", "contact", "msisdn", "imei"}:
        return "PHONE"
    if k in {"caller", "receiver"}:
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) >= 7 and not any(c.isalpha() for c in v):
            return "PHONE"
        return "PERSON"
    if k in {"vehicle_id", "registration", "vehicle", "car", "plate"}:
        return "VEHICLE"
    if k in {"location", "place", "city", "cell_tower"}:
        return "LOCATION"
    if k in {"account", "sender", "receiver_account", "bank_account", "account_id"}:
        return "ACCOUNT"
    if k in {"person_id", "person", "owner", "name", "suspect", "witness", "alias"}:
        return "PERSON"
    return "OTHER"


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
        keys_to_check = [
            "caller", "receiver", "sender", "receiver_account", "owner",
            "person_id", "person", "name", "vehicle_id", "registration", "vehicle",
            "location", "account", "phone", "mobile", "phone_number"
        ]
        for key in keys_to_check:
            if key == "person_id" and data.get("name"):
                continue
            if data.get(key):
                val = str(data[key]).strip()
                entity_type = _infer_entity_type(key, val)
                entities.append((entity_type, val))
        [resolve_or_create_entity(case_id, entity_type, name) for entity_type, name in entities]
        entity_ids = {}
        for key in keys_to_check:
            if data.get(key):
                val = str(data[key]).strip()
                entity_type = _infer_entity_type(key, val)
                entity_ids[key] = resolve_or_create_entity(case_id, entity_type, val)
        for relationship in relations_from_record(data, entity_ids):
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
