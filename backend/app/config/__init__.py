import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = Path(os.getenv("NEXUS_DB_PATH", ROOT_DIR / "nexus.db"))
DEFAULT_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "NEXUS_FRONTEND_ORIGINS",
        ",".join(DEFAULT_FRONTEND_ORIGINS),
    ).split(",")
    if origin.strip()
]
SERVE_FRONTEND = os.getenv("NEXUS_SERVE_FRONTEND", "false").lower() == "true"
