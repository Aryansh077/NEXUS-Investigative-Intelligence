from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import FRONTEND_ORIGINS, SERVE_FRONTEND
from .database.db import init_db

# Routers
from .api.auth import router as auth_router
from .api.cases import router as cases_router
from .api.complaints import router as complaints_router
from .api.predictions import router as predictions_router
from .api.heatmap import router as heatmap_router
from .api.financial import router as financial_router
from .api.alerts import router as alerts_router
from .api.evidence import router as evidence_router
from .api.rag import router as rag_router
from .api.model_eval import router as model_router
from .api.users import router as users_router
from .api.audit import router as audit_router

# Legacy / Graph Routers
from .api.entities import router as entities_router
from .api.graph import router as graph_router
from .api.timeline import router as timeline_router
from .api.anomalies import router as anomalies_router
from .api.copilot import router as copilot_router
from .api.ingestion import router as ingestion_router

app = FastAPI(
    title="NEXUS-PREDICT API",
    description="AI-Powered Cybercrime Cash-Out Prediction & Intelligence Platform.",
    version="1.0.0"
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

# Core NEXUS-PREDICT API Endpoints
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(cases_router, prefix="/api/cases", tags=["cases"])
app.include_router(complaints_router, prefix="/api/complaints", tags=["complaints"])
app.include_router(predictions_router, prefix="/api/predictions", tags=["predictions"])
app.include_router(heatmap_router, prefix="/api/heatmap", tags=["heatmap"])
app.include_router(financial_router, prefix="/api/financial", tags=["financial"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(evidence_router, prefix="/api/evidence", tags=["evidence"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
app.include_router(model_router, prefix="/api/model", tags=["model"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(audit_router, prefix="/api/audit", tags=["audit"])

# Network Graph & Ingestion Scaffolding
app.include_router(entities_router, prefix="/api/entities", tags=["entities"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])
app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])
app.include_router(anomalies_router, prefix="/api/anomalies", tags=["anomalies"])
app.include_router(copilot_router, prefix="/api/copilot", tags=["copilot"])
app.include_router(ingestion_router, prefix="/api/ingestion", tags=["ingestion"])

if SERVE_FRONTEND:
    frontend_assets = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "assets"
    if frontend_assets.exists():
        app.mount("/assets", StaticFiles(directory=frontend_assets), name="assets")

@app.get("/")
def root():
    frontend_index = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"
    if SERVE_FRONTEND and frontend_index.exists():
        return FileResponse(frontend_index)
    return {"name": "NEXUS-PREDICT", "status": "running", "data_mode": "synthetic"}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "nexus-predict-api",
        "model": "LightGBM Spatio-Temporal Cashout Predictor",
        "data_mode": "synthetic",
        "version": "1.0.0"
    }

@app.get("/api/summary")
def summary():
    from .database.db import get_conn, init_db
    init_db()
    conn = get_conn()
    counts = {
        "cases": conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0],
        "complaints": conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
        "transactions": conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
        "atms": conn.execute("SELECT COUNT(*) FROM atms").fetchone()[0],
        "locations": conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0],
        "predictions": conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0],
        "alerts": conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],
        "evidence": conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
    }
    conn.close()
    return counts
