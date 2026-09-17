# Architecture

```text
Synthetic CSV/TXT files
        |
        v
Ingestion and normalization -> SQLite evidence store
        |
        +-> entity and relationship extraction
        +-> NetworkX graph analytics
        +-> Isolation Forest anomaly leads
        +-> evidence-grounded Copilot retrieval
        |
        v
FastAPI JSON API -> React/Vite investigator workspace
```

The prototype keeps SQLite as the local persistence boundary. The service layer
does not require Neo4j or an external language model, so the demo remains
repeatable offline. Neo4j schemas and queries are kept separately for a future
deployment that needs distributed graph persistence.