# NEXUS Engineering Rules

NEXUS is an evidence-first investigative decision-support prototype using only
synthetic data. Never describe an anomaly as proof of criminality and never
invent evidence, model metrics, or training results.

Keep backend API contracts synchronized with the frontend. Add tests for
ingestion, analytics, security, and ML behavior. Use environment variables for
deployment configuration and do not commit credentials or private data.