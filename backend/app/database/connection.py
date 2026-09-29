"""
Database Connection & Session Factory for NEXUS-PREDICT
Supports PostgreSQL + PostGIS (via DATABASE_URL) and SQLite fallback.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from ..config import ROOT_DIR, DATABASE_PATH

DB_URL = os.getenv("NEXUS_DB_URL")
if not DB_URL:
    # Use SQLite fallback pointing to data/nexus.db or configured path
    sqlite_path = Path(DATABASE_PATH)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    DB_URL = f"sqlite:///{sqlite_path.resolve()}"

# Configure engine with connect_args for SQLite threading if needed
engine_args = {}
if DB_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DB_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Create all tables defined in SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
