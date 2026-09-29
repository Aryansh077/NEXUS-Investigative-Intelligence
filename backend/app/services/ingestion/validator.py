"""
Data Ingestion Validation & Quality Assessment Service
Validates CSV/JSON cybercrime records, detects duplicates, flags missing fields,
and generates structured Data Quality Reports.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import hashlib
import json

REQUIRED_FIELDS = {
    "complaints": ["complaint_id", "case_id", "victim_name", "crime_category", "fraud_amount"],
    "transactions": ["transaction_id", "case_id", "sender_account", "receiver_account", "amount", "timestamp"],
    "withdrawals": ["withdrawal_id", "case_id", "account_number", "atm_id", "amount", "timestamp"],
    "accounts": ["account_number", "holder_name", "bank_name"],
    "atms": ["atm_id", "cluster_id", "bank_name", "latitude", "longitude"],
}

def record_hash(record: Dict[str, Any], key_fields: List[str]) -> str:
    """Generate a unique fingerprint for duplicate detection."""
    content = "|".join(str(record.get(k, "")).strip().lower() for k in key_fields)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def validate_and_profile_data(
    records: List[Dict[str, Any]],
    dataset_type: str = "complaints"
) -> Dict[str, Any]:
    """
    Validates a batch of ingested records and generates a Data Quality Report.
    """
    total = len(records)
    accepted = []
    rejected = []
    validation_errors = []
    missing_fields_summary: Dict[str, int] = {}
    seen_hashes = set()
    duplicates_count = 0

    required = REQUIRED_FIELDS.get(dataset_type, ["case_id"])
    key_fields = required[:2] if len(required) >= 2 else required

    for idx, rec in enumerate(records):
        errors = []
        rec_id = rec.get("id") or rec.get(f"{dataset_type[:-1]}_id") or f"row-{idx+1}"

        # 1. Missing required fields check
        missing = [f for f in required if not str(rec.get(f, "")).strip()]
        if missing:
            for m in missing:
                missing_fields_summary[m] = missing_fields_summary.get(m, 0) + 1
            errors.append(f"Missing required fields: {', '.join(missing)}")

        # 2. Duplicate detection
        h = record_hash(rec, key_fields)
        if h in seen_hashes:
            duplicates_count += 1
            errors.append("Duplicate record identified by key fingerprint")
        else:
            seen_hashes.add(h)

        # 3. Numeric constraints
        for num_field in ["amount", "fraud_amount", "latitude", "longitude"]:
            if num_field in rec and str(rec.get(num_field, "")).strip():
                try:
                    val = float(rec[num_field])
                    if num_field in ["amount", "fraud_amount"] and val < 0:
                        errors.append(f"Field '{num_field}' cannot be negative: {val}")
                except ValueError:
                    errors.append(f"Field '{num_field}' must be a valid number, got '{rec[num_field]}'")

        if errors:
            rejected.append({"record_id": rec_id, "errors": errors, "raw": rec})
            validation_errors.append({"row_index": idx + 1, "record_id": rec_id, "issues": errors})
        else:
            accepted.append(rec)

    quality_score = round((len(accepted) / total * 100), 2) if total > 0 else 100.0

    return {
        "dataset_type": dataset_type,
        "total_records": total,
        "accepted_records": len(accepted),
        "rejected_records": len(rejected),
        "duplicates": duplicates_count,
        "missing_fields": missing_fields_summary,
        "validation_errors": validation_errors[:20],  # cap sample errors
        "data_quality_score": quality_score,
        "accepted_data": accepted
    }
