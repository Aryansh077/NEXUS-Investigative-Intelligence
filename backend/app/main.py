from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import FRONTEND_ORIGINS, SERVE_FRONTEND
from .database.db import init_db
from .api.auth import router as auth_router
from .api.cases import router as cases_router
from .api.entities import router as entities_router
from .api.graph import router as graph_router
from .api.evidence import router as evidence_router
from .api.timeline import router as timeline_router
from .api.anomalies import router as anomalies_router
from .api.copilot import router as copilot_router
from .api.ingestion import router as ingestion_router
from .api.audit import router as audit_router

app = FastAPI(
    title="NEXUS API",
    description="Evidence-first investigative intelligence prototype using synthetic data.",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(cases_router, prefix="/api/cases", tags=["cases"])
app.include_router(entities_router, prefix="/api/entities", tags=["entities"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])
app.include_router(evidence_router, prefix="/api/evidence", tags=["evidence"])
app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])
app.include_router(anomalies_router, prefix="/api/anomalies", tags=["anomalies"])
app.include_router(copilot_router, prefix="/api/copilot", tags=["copilot"])
app.include_router(ingestion_router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(audit_router, prefix="/api/audit", tags=["audit"])

if SERVE_FRONTEND:
    frontend_assets = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "assets"
    if frontend_assets.exists():
        app.mount("/assets", StaticFiles(directory=frontend_assets), name="assets")

@app.get("/")
def root():
    frontend_index = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"
    if SERVE_FRONTEND and frontend_index.exists():
        return FileResponse(frontend_index)
    return {"name": "NEXUS", "status": "running", "data_mode": "synthetic"}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "nexus-api", "data_mode": "synthetic"}


@app.get("/api/summary")
def summary():
    from .database.db import get_conn, init_db

    init_db()
    conn = get_conn()
    counts = {
        "cases": conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0],
        "entities": conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
        "relationships": conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0],
        "evidence": conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
        "anomalies": conn.execute("SELECT COUNT(*) FROM anomalies").fetchone()[0],
    }
    conn.close()
    return counts
