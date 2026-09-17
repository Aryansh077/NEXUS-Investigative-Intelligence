# NEXUS — Evidence-First Investigative Intelligence (Local Prototype)

This is a local, synthetic-data prototype for an SIH-style demonstration.
It does NOT connect to real police systems and should not be used with real
criminal/intelligence data.

## What works

- FastAPI backend
- Local SQLite database
- Synthetic case/data generator
- CSV ingestion for CDR, transactions, vehicles and locations
- Simple PDF/TXT/DOCX text ingestion hooks
- Local NER-style extraction (regex + deterministic rules)
- Entity resolution with fuzzy matching
- Relationship/event extraction
- Network analysis: degree, betweenness, communities, shortest paths
- Temporal timeline
- Explainable anomaly detection using Isolation Forest
- Evidence/provenance records
- Human verification state for relationships/findings
- Copilot that answers using retrieved local case data (no external AI required)
- React/Vite frontend
- Interactive Cytoscape graph
- Dashboard, case workspace, graph, timeline, entities, evidence, anomalies and copilot views
- Security-oriented RBAC and audit-log scaffolding

## Quick start

### Requirements

- Python 3.11+
- Node.js 20+

### Backend

Windows PowerShell:

```powershell
Set-Location 'L:\NEXUS_working_prototype\backend'
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ..\scripts\generate_data.py
python ..\scripts\seed_database.py
python -m uvicorn app.main:app --reload --port 8000
```

If PowerShell activation is blocked:

```powershell
Set-Location 'L:\NEXUS_working_prototype\backend'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ..\scripts\generate_data.py
.\.venv\Scripts\python.exe ..\scripts\seed_database.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Frontend

Open another terminal:

```powershell
Set-Location 'L:\NEXUS_working_prototype\frontend'
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Open the URL printed by Vite, normally:
http://localhost:5173

The backend API is normally:
http://localhost:8000
Swagger docs:
http://localhost:8000/docs

### Docker deployment

From the repository root, build and start the single-container demo:

```powershell
docker compose up --build
```

Open http://localhost:8000. The container serves the built frontend and API
together, and persists the synthetic SQLite database in the `nexus-data` volume.
The container is intended for local demonstration, not production deployment.

Health check:
http://localhost:8000/api/health

## Demo login

This prototype uses a local demo login:

- username: investigator
- password: nexus-demo

This is intentionally NOT production authentication.

## Prototype architecture

Synthetic data -> ingestion -> normalization -> extraction -> entity resolution
-> graph -> analytics -> evidence -> copilot -> human verification.

## Security note

The local prototype deliberately uses synthetic data and a local rule-based/retrieval
Copilot. For a real deployment, replace the demo auth, add proper RBAC/ABAC,
encryption at rest/in transit, secrets management, audit controls, secure storage,
network isolation, model governance and authorized institutional data connectors.

Never upload real police, intelligence, CDR, financial or personally identifying
investigative data into this prototype.

## Team workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for the GitHub branch workflow and
[docs/TEAM_TASKS.md](docs/TEAM_TASKS.md) for six-member ownership.
