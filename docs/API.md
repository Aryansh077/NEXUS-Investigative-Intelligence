# API

The local API runs at `http://localhost:8000` and exposes Swagger at `/docs`.

## System

- `GET /api/health` returns service status.
- `GET /api/summary` returns counts for seeded records.

## Investigation

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `GET /api/entities/{case_id}`
- `GET /api/graph/{case_id}`
- `GET /api/graph/{case_id}/metrics`
- `GET /api/graph/{case_id}/path?source=...&target=...`
- `GET /api/timeline/{case_id}`
- `GET /api/evidence/{case_id}`
- `GET /api/anomalies/{case_id}`
- `POST /api/copilot/ask`
- `POST /api/ingestion/{case_id}`
- `GET /api/audit`
- `GET /api/audit/{case_id}`

All data in the prototype is synthetic. Analytical results are leads for human
review and are not determinations of guilt or criminality.