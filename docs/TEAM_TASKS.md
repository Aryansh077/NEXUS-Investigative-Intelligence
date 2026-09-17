# Team Tasks

This ownership split follows the six-member team structure. Each member works on
their feature branch and opens a pull request into `main`.

## Member 1: DIKSHA - Data Ingestion and Backend

Branch: `feature/ingestion-backend`

Owns `backend/app/api/ingestion.py`, `backend/app/services/ingestion/`, database
initialization, structured schemas, upload validation, and `scripts/seed_database.py`.

## Member 2: SANIKA - NLP and Entity Resolution

Branch: `feature/nlp-resolution`

Owns `backend/app/services/nlp/`, `backend/app/services/entity_resolution/`,
and relationship extraction interfaces used by ingestion.

## Member 3: SAMIKSHA - Knowledge Graph

Branch: `feature/knowledge-graph`

Owns `backend/app/services/graph/` and `neo4j/`.

## Member 4: MADHURA - ML and Anomaly Detection

Branch: `feature/ml-anomaly`

Owns `ml/` and `backend/app/services/anomaly/`.

## Member 5: SRINIDHI - Frontend and Visualization

Branch: `feature/frontend-visualization`

Owns `frontend/`.

## Member 6: ARYANSH - Copilot, Security, and Integration

Branch: `feature/copilot-security`

Owns `backend/app/services/copilot/`, `backend/app/security/`, audit behavior,
integration tests, Docker, and CI coordination.

## Collaboration rules

- Do not develop directly on `main`.
- Keep commits focused and explain behavior changes in pull requests.
- Update frontend API calls and backend tests when an API contract changes.
- Never commit `.env`, `.venv`, `node_modules`, databases, credentials, or private data.
- Run backend tests and frontend build before opening a pull request.