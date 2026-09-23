import os
import sqlite3
from pathlib import Path
from ..config import DATABASE_PATH

DB_PATH = DATABASE_PATH

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
    anomaly_columns = {row[1] for row in conn.execute("PRAGMA table_info(anomalies)").fetchall()}
    for column, definition in {
        "verification": "TEXT DEFAULT 'pending'",
        "reviewed_by": "TEXT",
        "reviewed_at": "TEXT",
        "review_note": "TEXT",
    }.items():
        if column not in anomaly_columns:
            conn.execute(f"ALTER TABLE anomalies ADD COLUMN {column} {definition}")
    conn.commit()
    conn.close()
