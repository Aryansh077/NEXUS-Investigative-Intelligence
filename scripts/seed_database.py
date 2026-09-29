#!/usr/bin/env python3
"""
NEXUS-PREDICT Database Seeder
Seeds SQLite/Postgres with realistic synthetic cybercrime data,
complaints, accounts, transactions, ATM clusters, users, and evidence.
"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.database.connection import init_database, SessionLocal
from app.database.models import (
    User, Case, Complaint, Account, Transaction, Location, ATM,
    Withdrawal, Evidence, Entity, Relationship, AuditLog
)
from app.security.hashing import hash_password, sha256_text

DATA_DIR = ROOT / "data" / "synthetic"

def load_csv(filename):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"Warning: {path} not found.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def seed():
    print("=" * 60)
    print("NEXUS-PREDICT: Initializing Database & Seeding Synthetic Data...")
    print("=" * 60)

    # 1. Initialize schema and column migrations
    from app.database.db import init_db
    init_db()
    db = SessionLocal()

    # 2. Seed Users
    users_data = [
        ("USR-001", "admin", "nexus-admin", "admin", "System Administrator", "admin@nexus.internal"),
        ("USR-002", "investigator", "nexus-demo", "investigator", "Lead Cyber Investigator", "investigator@nexus.internal"),
        ("USR-003", "analyst", "nexus-analyst", "analyst", "Financial Intelligence Analyst", "analyst@nexus.internal"),
        ("USR-004", "viewer", "nexus-viewer", "viewer", "Case Observer", "viewer@nexus.internal"),
    ]
    for uid, uname, pwd, role, fname, email in users_data:
        existing = db.query(User).filter_by(username=uname).first()
        if not existing:
            db.add(User(
                id=uid,
                username=uname,
                hashed_password=hash_password(pwd),
                role=role,
                full_name=fname,
                email=email,
                is_active=True
            ))
    db.commit()
    print("  [+] Users seeded (admin, investigator, analyst, viewer).")

    # 3. Seed Locations
    locations_rows = load_csv("locations.csv")
    for row in locations_rows:
        existing = db.query(Location).filter_by(cluster_id=row["cluster_id"]).first()
        if not existing:
            db.add(Location(
                cluster_id=row["cluster_id"],
                cluster_name=row["cluster_name"],
                district=row["district"],
                city=row["city"],
                center_lat=float(row["center_lat"]),
                center_lon=float(row["center_lon"]),
                risk_tier=row["risk_tier"],
                historical_crime_density=float(row["historical_crime_density"]),
            ))
    db.commit()
    print(f"  [+] Locations seeded: {len(locations_rows)} clusters.")

    # 4. Seed ATMs
    atms_rows = load_csv("atms.csv")
    for row in atms_rows:
        existing = db.query(ATM).filter_by(atm_id=row["atm_id"]).first()
        if not existing:
            db.add(ATM(
                atm_id=row["atm_id"],
                cluster_id=row["cluster_id"],
                bank_name=row["bank_name"],
                ifsc=row["ifsc"],
                location_name=row["location_name"],
                district=row["district"],
                city=row["city"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                daily_cash_limit=float(row["daily_cash_limit"]),
                is_operational=row["is_operational"],
                cctv_available=row["cctv_available"],
                historical_fraud_count=int(row["historical_fraud_count"]),
            ))
    db.commit()
    print(f"  [+] ATMs seeded: {len(atms_rows)} ATMs.")

    # 5. Seed Cases
    cases_rows = load_csv("cases.csv")
    for row in cases_rows:
        existing = db.query(Case).filter_by(id=row["case_id"]).first()
        if not existing:
            db.add(Case(
                id=row["case_id"],
                title=row["title"],
                description=f"Syndicate: {row['syndicate_name']}. Target City: {row['city']}. Primary cash-out corridor: {row['primary_cluster']}.",
                category=row["category"],
                syndicate_name=row["syndicate_name"],
                city=row["city"],
                primary_cluster=row["primary_cluster"],
                status=row["status"],
                created_at=row["created_at"],
            ))
    db.commit()
    print(f"  [+] Cases seeded: {len(cases_rows)} cases.")

    # 6. Seed Accounts
    accounts_rows = load_csv("accounts.csv")
    for row in accounts_rows:
        existing = db.query(Account).filter_by(account_number=row["account_number"]).first()
        if not existing:
            db.add(Account(
                account_number=row["account_number"],
                holder_name=row["holder_name"],
                bank_name=row["bank_name"],
                ifsc=row["ifsc"],
                account_type=row["account_type"],
                role=row["role"],
                city=row["city"],
                upi_id=row["upi_id"],
                risk_tier=row["risk_tier"],
                created_date=row["created_date"],
                status=row["status"],
            ))
    db.commit()
    print(f"  [+] Accounts seeded: {len(accounts_rows)} accounts.")

    # 7. Seed Complaints
    complaints_rows = load_csv("complaints.csv")
    for row in complaints_rows:
        existing = db.query(Complaint).filter_by(id=row["complaint_id"]).first()
        if not existing:
            db.add(Complaint(
                id=row["complaint_id"],
                case_id=row["case_id"],
                victim_name=row["victim_name"],
                victim_phone=row["victim_phone"],
                victim_account=row["victim_account"],
                crime_category=row["crime_category"],
                fraud_amount=float(row["fraud_amount"]),
                incident_timestamp=row["incident_timestamp"],
                narrative=row["narrative"],
                status=row["status"],
                city=row["city"],
            ))
            # Also create an initial tamper-evident Evidence record for the complaint
            sha = sha256_text(row["narrative"])
            db.add(Evidence(
                id=f"EV-CMP-{row['complaint_id']}",
                case_id=row["case_id"],
                record_type="complaint_fir",
                title=f"Initial Cyber Complaint {row['complaint_id']} Narrative",
                content=row["narrative"],
                timestamp=row["incident_timestamp"],
                source_file="complaints.csv",
                hash=sha,
                uploader="ncrp_ingestion_daemon"
            ))
    db.commit()
    print(f"  [+] Complaints seeded: {len(complaints_rows)} complaints.")

    # 8. Seed Transactions
    tx_rows = load_csv("transactions.csv")
    for row in tx_rows:
        existing = db.query(Transaction).filter_by(id=row["transaction_id"]).first()
        if not existing:
            db.add(Transaction(
                id=row["transaction_id"],
                case_id=row["case_id"],
                complaint_id=row["complaint_id"],
                sender_account=row["sender_account"],
                receiver_account=row["receiver_account"],
                amount=float(row["amount"]),
                timestamp=row["timestamp"],
                channel=row["channel"],
                hop_level=int(row["hop_level"]),
                status=row["status"],
                velocity_score=float(row["velocity_score"]),
            ))
    db.commit()
    print(f"  [+] Transactions seeded: {len(tx_rows)} multi-hop transfers.")

    # 9. Seed Withdrawals
    w_rows = load_csv("withdrawals.csv")
    for row in w_rows:
        existing = db.query(Withdrawal).filter_by(id=row["withdrawal_id"]).first()
        if not existing:
            db.add(Withdrawal(
                id=row["withdrawal_id"],
                case_id=row["case_id"],
                complaint_id=row["complaint_id"],
                account_number=row["account_number"],
                atm_id=row["atm_id"],
                cluster_id=row["cluster_id"],
                amount=float(row["amount"]),
                timestamp=row["timestamp"],
                card_id=row["card_id"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
            ))
    db.commit()
    print(f"  [+] Withdrawals seeded: {len(w_rows)} ATM cash withdrawals.")

    # 10. Populate Graph Entities & Relationships from accounts & transactions
    for acc in accounts_rows:
        eid = f"ENT-ACC-{acc['account_number']}"
        existing = db.query(Entity).filter_by(id=eid).first()
        if not existing:
            db.add(Entity(
                id=eid,
                case_id="CASE-1021",  # Link or distribute across cases
                type="ACCOUNT",
                name=f"{acc['account_number']} ({acc['holder_name']})",
                metadata_json=json.dumps({"role": acc["role"], "bank": acc["bank_name"], "risk": acc["risk_tier"]})
            ))
    for row in tx_rows[:60]:
        rid = f"REL-{row['transaction_id']}"
        existing = db.query(Relationship).filter_by(id=rid).first()
        if not existing:
            src_id = f"ENT-ACC-{row['sender_account']}"
            tgt_id = f"ENT-ACC-{row['receiver_account']}"
            db.add(Relationship(
                id=rid,
                case_id=row["case_id"],
                source_id=src_id,
                target_id=tgt_id,
                type=f"TRANSFER_HOP_{row['hop_level']}",
                confidence=0.99,
                timestamp=row["timestamp"],
                source_record=f"TX {row['transaction_id']} (INR {float(row['amount']):,})",
                verification="verified",
                metadata_json=json.dumps({"amount": float(row["amount"]), "channel": row["channel"]})
            ))
    db.commit()

    # 11. Initial Audit Log
    db.add(AuditLog(
        username="system",
        action="SEED_DATABASE",
        case_id="ALL",
        target_id="DATABASE",
        details_json=json.dumps({"seeded_tables": ["users", "locations", "atms", "cases", "accounts", "complaints", "transactions", "withdrawals"]}),
        timestamp=datetime.now(timezone.utc).isoformat()
    ))
    db.commit()
    db.close()

    print("=" * 60)
    print("Database seeding completed successfully.")
    print("=" * 60)

if __name__ == "__main__":
    seed()
