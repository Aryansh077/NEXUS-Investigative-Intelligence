# NEXUS-PREDICT: Platform Architecture, Technology Stack & Presentation Guide

**Smart India Hackathon (SIH) — Comprehensive Technical & Presentation Dossier**

---

## 1. Executive Summary & Problem Statement

### The Critical Cybercrime Bottleneck
In financial cyber fraud (UPI scams, APK malware, "digital arrests", investment frauds), **the most time-sensitive point of failure for law enforcement is the physical cash-out**. 
Once stolen funds enter the banking system, criminals rapidly disperse money across layered "mule" accounts (Layer-1, Layer-2 smurfing) and dispatch field operatives to withdraw cash at automated teller machines (ATMs) before bank freeze orders or NCRP portal alerts can take effect.

### The Objective of NEXUS-PREDICT
NEXUS-PREDICT is an **AI-powered investigative intelligence platform** that analyzes incoming cybercrime complaints, transaction velocity, and historical syndicate behavior to:

$$\textbf{PREDICT WHERE AND WHEN A CASH WITHDRAWAL IS LIKELY TO OCCUR}$$

The system produces **ranked candidate ATM clusters**, calibrated risk scores ($0–100$), estimated temporal withdrawal windows (e.g., `14:00–18:00`), and explainable AI feature drivers to empower field officers to interdict funds **before** cash leaves the ATM.

---

## 2. Technology Stack & Component Mapping

| Layer | Technology | Exact Role & Justification |
| :--- | :--- | :--- |
| **Frontend UI** | **React 18 + Vite** | High-performance, reactive single-page command center; fast component re-rendering and low bundle overhead. |
| **Frontend Styling** | **Tailwind CSS + CSS Design System** | Custom dark command-center aesthetic (`#070d18` / `#091220`), high-contrast tactical accents, glassmorphic panels, and responsive layout. |
| **GIS Heatmap** | **Leaflet (v1.9.4)** | Interactive geospatial mapping; renders ATM clusters, variable-radius risk heat buffers, and individual ATM pins with CCTV coverage. |
| **Network Graph** | **Cytoscape.js (v3.31)** | Interactive directed graph visualization of multi-hop money laundering (Victim $\to$ Mule L1 $\to$ Mule L2 $\to$ ATM Cash-Out). |
| **Icons & Visuals**| **Lucide React** | Lightweight, SVG-based icons for all tactical status indicators, roles, and actions. |
| **Backend API** | **Python 3.10+ & FastAPI** | Asynchronous, high-throughput REST API with automatic OpenAPI (Swagger) generation and native typing. |
| **Data Validation**| **Pydantic (v2.10)** | Strict schema validation, request/response models, and type safety across all API routes. |
| **Database ORM** | **SQLAlchemy (v2.0)** | Object-relational mapping supporting PostgreSQL + PostGIS in production, with transparent SQLite fallback (`nexus.db`) for zero-dependency local runs. |
| **Primary ML** | **LightGBM (v4.7.0)** | Primary champion gradient boosted decision tree classifier; predicts withdrawal probability with **ROC-AUC: 0.9286** and **2.05 ms latency**. |
| **Baseline ML** | **Scikit-learn (v1.6.0)** | Logistic Regression baseline model, Random Forest classifier, and multi-metric ranking evaluators. |
| **Explainable AI** | **TreeSHAP (SHAP v0.49)** | Computes Shapley feature contribution values per candidate prediction to explain *why* an ATM cluster was ranked highly. |
| **Cybercrime NLP** | **spaCy & Pattern Engine** | Extracts crime category, fraud amount, dates, banks, account references, IFSC codes, UPI handles, and locations with confidence scoring. |
| **Entity Matcher** | **RapidFuzz (v3.11)** | High-speed Levenshtein fuzzy string matching for suspect aliases, phone numbers, and bank account numbers. |
| **Network Analysis**| **NetworkX (v3.4)** | Graph algorithms for degree centrality, betweenness, and shortest path traversal across financial networks. |
| **Graph DB** | **Neo4j + Cypher** | Graph traversal schema ready for deep multi-tier shell company and mule ring traversals. |
| **RAG Assistant** | **Local Grounded Retrieval** | Evidence-grounded retrieval engine with anti-hallucination safeguard: strictly answers from verified case chunks or returns *"No supporting record was found."* |
| **Evidence Security**| **SHA-256 Cryptography** | Tamper-evident cryptographic hashing on evidence records with live UI recalculation to detect data manipulation. |
| **Authentication** | **JWT & Bcrypt** | Secure JSON Web Tokens with role-based access control (`admin`, `investigator`, `analyst`, `viewer`). |
| **Testing** | **Pytest & TestClient** | 16-test automated suite covering predictions, money flow, RAG, metrics, and security. |
| **Containerization**| **Docker & Docker Compose**| Multi-stage container builds packaging the FastAPI backend, built frontend dist, and synthetic seed database. |

---

## 3. End-to-End System Architecture & Flow

```
                      ┌────────────────────────────────────────────────────────┐
                      │                 CYBERCRIME COMPLAINT                   │
                      │         Victim Narrative, Amount, Bank Details         │
                      └───────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
                      ┌────────────────────────────────────────────────────────┐
                      │              DATA INGESTION & PROFILING                │
                      │   Validation, Deduplication, Data Quality Scoring      │
                      └───────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
                      ┌────────────────────────────────────────────────────────┐
                      │             CYBERCRIME NLP & ENTITY RESOLUTION         │
                      │  Extracts Crime Type, Loss, Accounts, UPI, IFSC, Phone │
                      └───────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
                      ┌────────────────────────────────────────────────────────┐
                      │            FINANCIAL MONEY-FLOW TRACER                 │
                      │   Traces Victim -> Mule L1 -> Mule L2 -> ATM Cash-Out  │
                      └───────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
                      ┌────────────────────────────────────────────────────────┐
                      │            SPATIO-TEMPORAL FEATURE PIPELINE            │
                      │  12 Features: Temporal, Velocity, Distance, Density    │
                      └───────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
                      ┌────────────────────────────────────────────────────────┐
                      │          PYTHON ML PREDICTOR (LightGBM)                │
                      │  Ranks Locations, Calibrates Risk (0-100), Time Window │
                      └──────────────┬──────────────────────────┬──────────────┘
                                     │                          │
                                     ▼                          ▼
               ┌───────────────────────────────┐     ┌─────────────────────────┐
               │    EXPLAINABLE AI (TreeSHAP)  │     │      ALERT ENGINE       │
               │  Feature Signal Contributions │     │  Threshold-based alerts │
               └──────────────┬────────────────┘     └──────────┬──────────────┘
                              │                                 │
                              └────────────────┬────────────────┘
                                               │
                                               ▼
                      ┌────────────────────────────────────────────────────────┐
                      │         GIS RISK HEATMAP & COMMAND DASHBOARD           │
                      │   Leaflet Spatial Radius, Predictions, Cytoscape Graph │
                      └────────────────────────┬───────────────────────────────┘
                                               │
                                               ▼
                      ┌────────────────────────────────────────────────────────┐
                      │           GROUNDED RAG INVESTIGATION ASSISTANT         │
                      │   Evidence-backed answers with zero hallucinations     │
                      └────────────────────────────────────────────────────────┘
```

---

## 4. Spatio-Temporal Prediction & Machine Learning Engine

### The 12 Predictive Features (`ml/features/feature_pipeline.py`)

1. **`fraud_amount_log`**: Log-scaled stolen amount (larger fraud induces rapid dispersal).
2. **`incident_hour`**: Hour of complaint reporting (0–23).
3. **`is_weekend`**: Flag for bank closure days when branch liquidation is impossible.
4. **`hours_since_incident`**: Time elapsed from first incident ping.
5. **`tx_velocity_max`**: Maximum velocity score of fund transfer hops.
6. **`tx_hop_count`**: Number of laundering layers detected.
7. **`cluster_crime_density`**: Historical cybercrime frequency in the candidate district.
8. **`cluster_atm_count`**: Density of ATMs in the candidate cluster.
9. **`distance_to_complaint_km`**: Great-circle Haversine distance from incident origin to ATM cluster.
10. **`historical_cluster_recurrence`**: Recurrence frequency of cash-outs in this cluster.
11. **`syndicate_cluster_affinity`**: Historical preference score of the identified syndicate for this corridor.
12. **`time_window_risk_alignment`**: Evening/night alignment flag (18:00–02:00 ATM limit rollover).

### True Model Evaluation Results (`ml/evaluation/metrics.json`)

*Evaluated strictly against synthetic ground truth (`ground_truth.json`). Never hard-coded:*

| Metric | Logistic Regression (Baseline) | Random Forest | LightGBM (Champion) |
| :--- | :---: | :---: | :---: |
| **ROC-AUC** | 0.8956 | 0.8866 | **0.9286** |
| **PR-AUC** | 0.7101 | 0.7138 | **0.7586** |
| **Top-1 Location Hit Rate** | 81.82% | 81.82% | **81.82%** |
| **Top-3 Location Hit Rate** | 81.82% | 81.82% | **81.82%** |
| **Top-5 Location Hit Rate** | 81.82% | 81.82% | **100.0%** |
| **Inference Latency** | ~1.2 ms | ~4.8 ms | **2.05 ms** |

---

## 5. Live Demonstration Script for Hackathon Jury

### Step 1: Login & Role-Based Access Control
- Navigate to `http://localhost:5173`.
- Click the **Investigator** demo button (`nexus-demo`).
- Highlight: The platform uses JWT session tokens and enforces strict RBAC (`admin`, `investigator`, `analyst`, `viewer`).

### Step 2: Executive Intelligence Dashboard
- Review high-level KPIs: Ingested Complaints (44), Total Fraud Volume (₹1.7Cr+), High-Risk ATM Clusters (4), and Active Interdiction Alerts.
- Point out the Top-5 Location Hit Rate (100.0%) and the live ATM risk heatmap preview.

### Step 3: Trigger Live Spatio-Temporal Prediction
- Select complaint **`C1001`** (Victim defrauded of ₹1,20,000 under Card Skimming / OTP Fraud in Mumbai).
- Click **"Predict Cash-Out"**:
  - The live Python LightGBM model executes inference in ~2 milliseconds.
  - Ranked locations appear:
    - **Rank #1**: Andheri West Lokhandwala Hub $\to$ Risk **89/100** • Window: **14:00–18:00**
    - **Rank #2**: Bandra Kurla Complex Tech Zone $\to$ Risk **67/100** • Window: **14:00–18:00**
    - **Rank #3**: Kothrud Paud Road Corridor $\to$ Risk **18/100**
- Highlight: **TreeSHAP** explains why Andheri West is Rank #1 (Syndicate cluster affinity +0.42, ATM density +0.28).

### Step 4: Explore GIS Risk Heatmap
- Navigate to **GIS Risk Heatmap**:
  - Observe ATM clusters across Delhi-NCR, Mumbai, Pune, and Bengaluru.
  - Click on the Andheri West cluster: see circular risk heat buffer (red), 5 monitored ATMs, CCTV coverage flags, and operational status.

### Step 5: Trace Multi-Hop Money Flow
- Navigate to **Money Flow**:
  - View the interactive Cytoscape graph:
    `Victim Account` $\to$ `Mule L1 (ACC-SYN-MUM-01-L1-01)` $\to$ `Mule L2 (ACC-SYN-MUM-01-L2-01)` $\to$ `ATM-123 Cash-Out`.
  - Point out transaction velocity scores and liquidation percentage (87.5%).

### Step 6: Review Alerts & Evidence Integrity
- Navigate to **Alert Center**: See the automated Critical Alert triggered for Andheri West; update status from `New` to `Investigating`.
- Navigate to **Evidence Vault**: Show the cryptographic **SHA-256 hash** (`1836a6b...`) for the complaint narrative; click **"Verify Integrity"** to demonstrate tamper detection.

### Step 7: Grounded RAG Assistant
- Navigate to **RAG Assistant**:
  - Ask: *"Why was this location ranked highly and what evidence supports it?"*
  - The assistant retrieves verified case facts and cites exact evidence IDs and predictions with **zero hallucinations**.

### Step 8: Model Evaluation Transparency
- Navigate to **Model Evaluation**: Show the side-by-side benchmark comparison table proving that performance metrics come from genuine ground-truth calculation, not fake hardcoding.

---

## 6. How to Run Locally

```powershell
# 1. Start Backend & ML Services
Set-Location 'L:\NEXUS_working_prototype\backend'
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000

# 2. Start Frontend Command Center
Set-Location 'L:\NEXUS_working_prototype\frontend'
npm run dev

# 3. Run Automated Tests
Set-Location 'L:\NEXUS_working_prototype\backend'
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 7. SIH Jury FAQ Cheatsheet

**Q: Are these predictions hard-coded?**
> *No. Every prediction is computed on the fly by `ml/inference/predictor.py` executing the trained LightGBM model (`champion_lightgbm.joblib`) against feature matrices extracted from the complaint and candidate ATM coordinates.*

**Q: How do you prevent RAG hallucinations?**
> *The RAG assistant operates under strict lexical and semantic bounding. It only synthesizes answers from verified database chunks and returns "No supporting record was found." if context is absent.*

**Q: Why LightGBM over Deep Learning?**
> *Tabular financial, spatio-temporal, and categorical metadata (IFSC, bank, velocity) perform best on gradient boosted trees. LightGBM provides 2.05 ms inference latency, 100% Top-5 accuracy, and native TreeSHAP interpretability.*
