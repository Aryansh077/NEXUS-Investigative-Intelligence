import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("NEXUS_DB_PATH", Path(__file__).resolve().parents[3] / "nexus.db"))

def get_conn():
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
        created_at TEXT
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
    conn.commit()
    conn.close()
