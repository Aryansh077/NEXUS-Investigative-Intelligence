import os
import sqlite3
from pathlib import Path
from ..config import DATABASE_PATH
from .connection import init_database

DB_PATH = DATABASE_PATH

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Initialize all SQLAlchemy tables (cases, complaints, accounts, transactions, atms, predictions, alerts, etc.)
    init_database()

    # Ensure backward-compatible SQLite columns for existing anomalies table
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'Active',
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        metadata_json TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS relationships (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        type TEXT NOT NULL,
        confidence REAL DEFAULT 0.5,
        timestamp TEXT,
        source_record TEXT,
        verification TEXT DEFAULT 'pending',
        metadata_json TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS evidence (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        record_type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        timestamp TEXT,
        source_file TEXT,
        hash TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS anomalies (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        score REAL,
        severity TEXT,
        reason TEXT,
        created_at TEXT,
        verification TEXT DEFAULT 'pending',
        reviewed_by TEXT,
        reviewed_at TEXT,
        review_note TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        case_id TEXT,
        target_id TEXT,
        timestamp TEXT
    );
    """)
    # Ensure backward-compatible SQLite columns for existing cases table
    case_columns = {row[1] for row in conn.execute("PRAGMA table_info(cases)").fetchall()}
    for column, definition in {
        "category": "TEXT DEFAULT 'Cybercrime'",
        "syndicate_name": "TEXT",
        "city": "TEXT",
        "primary_cluster": "TEXT",
    }.items():
        if column not in case_columns:
            conn.execute(f"ALTER TABLE cases ADD COLUMN {column} {definition}")

    # Ensure backward-compatible SQLite columns for existing anomalies table
    anomaly_columns = {row[1] for row in conn.execute("PRAGMA table_info(anomalies)").fetchall()}
    for column, definition in {
        "verification": "TEXT DEFAULT 'pending'",
        "reviewed_by": "TEXT",
        "reviewed_at": "TEXT",
        "review_note": "TEXT",
    }.items():
        if column not in anomaly_columns:
            conn.execute(f"ALTER TABLE anomalies ADD COLUMN {column} {definition}")

    # Ensure backward-compatible SQLite columns for audit_logs table
    audit_columns = {row[1] for row in conn.execute("PRAGMA table_info(audit_logs)").fetchall()}
    if "details_json" not in audit_columns:
        conn.execute("ALTER TABLE audit_logs ADD COLUMN details_json TEXT DEFAULT '{}'")
    conn.commit()
    conn.close()
