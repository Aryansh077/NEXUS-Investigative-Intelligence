# NEXUS-PREDICT: System Architecture

```text
                     CYBERCRIME COMPLAINT (NCRP/FIR)
                                  │
                                  ▼
                     DATA INGESTION & PROFILING
          (Deduplication, Field Verification, Quality Scoring)
                                  │
                                  ▼
                   CYBERCRIME NLP & ENTITY RESOLUTION
            (spaCy & Patterns: Loss, UPI, IFSC, Accounts, RapidFuzz)
                                  │
                                  ▼
                     FINANCIAL MONEY-FLOW TRACER
             (Victim -> Mule L1 -> Mule L2 -> ATM Cash-Out)
                                  │
                                  ▼
                 SPATIO-TEMPORAL FEATURE PIPELINE
             (12 Features: Temporal, Velocity, Spatial, Graph)
                                  │
                                  ▼
                  PYTHON ML PREDICTOR (LightGBM)
      (Ranks Candidate ATM Clusters, Calibrates Risk 0-100, Window)
                                  │
                                  ├────────────────────────┐
                                  ▼                        ▼
                       EXPLAINABLE AI (TreeSHAP)      ALERT ENGINE
                     (Feature Impact Contributions) (Threshold Alerts)
                                  │                        │
                                  └───────────┬────────────┘
                                              ▼
                             GIS RISK HEATMAP & COMMAND CENTER
                             (Leaflet Spatial Buffers, Cytoscape)
                                              │
                                              ▼
                                 GROUNDED RAG ASSISTANT
                           (Evidence-Backed Q&A, No Hallucinations)
```

## Architectural Highlights

1. **Decoupled Prediction vs Explanation**: 
   - Prediction is performed by real Python ML inference (`LightGBM`).
   - Explanation is powered by `TreeSHAP` feature attribution.
   - Narrative synthesis and case retrieval is performed by the RAG assistant with anti-hallucination constraints.

2. **Persistence Layer**:
   - Primary Relational: PostgreSQL / SQLite (`nexus.db`) via SQLAlchemy models.
   - Geospatial: PostGIS / Haversine distance matrix for radius and clustering queries.
   - Graph: NetworkX for in-memory traversal and Cytoscape rendering; Neo4j Cypher queries for multi-tier mule ring analysis.

3. **Security & Evidence Integrity**:
   - Every piece of uploaded or generated evidence is hashed using SHA-256 for cryptographic tamper-evidence.
   - Granular RBAC permissions for `admin`, `investigator`, `analyst`, and `viewer` roles backed by JWT tokens.