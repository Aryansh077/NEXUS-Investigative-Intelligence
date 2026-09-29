# NEXUS-PREDICT: AI-Powered Cybercrime Cash-Out Prediction & Intelligence Platform

**Smart India Hackathon (SIH) Prototype**

NEXUS-PREDICT is an end-to-end, evidence-first investigative decision-support platform designed to solve the critical cybercrime enforcement challenge: **Predicting WHERE and WHEN an illicit cash withdrawal / ATM cash-out is likely to occur** following a cyber fraud complaint.

> **Integrity & Compliance Note:** This platform uses realistic **synthetic and anonymized data only**. It does not invent evidence, hard-code predictions, or fabricate model metrics. All figures, locations, and rankings are calculated live from real Python ML inference.

---

## 1. Core Platform Capabilities

- **Realistic Synthetic Dataset:** Realistic Indian cybercrime complaints, accounts, multi-hop laundering chains (Victim → L1 Mule → L2 Mules → ATM Cash-Out), 57 ATMs across 12 metropolitan clusters (Delhi-NCR, Mumbai, Pune, Bengaluru), and `ground_truth.json`.
- **Cybercrime NLP:** Extracts crime types, fraud amounts, timestamps, banks, accounts, IFSC, UPI handles, and locations with confidence scoring.
- **Entity Resolution:** RapidFuzz fuzzy matching for accounts, phone numbers, and suspect aliases.
- **Financial & Money-Flow Tracer:** Traces multi-hop laundering chains, smurfing velocity, and liquidation ratios; visualized interactively via Cytoscape.js.
- **Feature Engineering Pipeline:** 12 spatio-temporal, financial velocity, ATM density, and historical recurrence features.
- **Python ML Spatio-Temporal Prediction:**
  - **Logistic Regression (Baseline)**: ROC-AUC 0.8956, Top-1 Hit Rate 81.8%
  - **Random Forest**: ROC-AUC 0.8866, Top-1 Hit Rate 81.8%
  - **LightGBM (Champion Model)**: ROC-AUC **0.9286**, PR-AUC **0.7586**, Top-1 Hit Rate **81.82%**, Top-5 Hit Rate **100.0%**, Avg. Latency **2.05 ms**.
- **Explainable AI (TreeSHAP):** Local feature attribution explaining why a location was ranked highly (syndicate affinity, crime density, ATM density, evening cash-out velocity).
- **Interactive GIS Risk Heatmap:** Powered by Leaflet; renders ATM clusters with circular risk radius, individual ATMs with CCTV coverage, and prediction windows.
- **Real-Time Alert Engine:** Threshold-based alerts with status lifecycle transitions (`New`, `Acknowledged`, `Investigating`, `Resolved`, `Dismissed`).
- **Grounded RAG Assistant:** Answers case questions strictly from verified evidence records, transactions, and predictions with anti-hallucination guard (*"No supporting record was found"*).
- **Evidence Integrity Ledger:** Tamper-evident cryptographic SHA-256 hashing with live verification.
- **Role-Based Access Control (RBAC):** `admin`, `investigator`, `analyst`, `viewer` roles with JWT authentication and audit trails.

---

## 2. Quick Start

### Prerequisites
- Python 3.10+
- Node.js 20+

### Option A: Local Development

#### 1. Backend & ML Setup
```powershell
Set-Location 'L:\NEXUS_working_prototype\backend'
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Generate synthetic dataset & ground truth benchmark
python ..\scripts\generate_synthetic_data.py

# Train models & evaluate Top-K performance
python ..\ml\training\train_models.py

# Seed database with complaints, accounts, ATMs, and users
python ..\scripts\seed_database.py

# Start FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```powershell
Set-Location 'L:\NEXUS_working_prototype\frontend'
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
Open **http://localhost:5173** in your browser.

---

### Option B: Docker Deployment
```powershell
Set-Location 'L:\NEXUS_working_prototype'
docker compose up --build
```
Open **http://localhost:8000** for the combined platform.

---

## 3. Demo Credentials (RBAC)

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Lead Investigator** | `investigator` | `nexus-demo` | Full investigation, predictions, alerts, RAG copilot, evidence |
| **System Administrator** | `admin` | `nexus-admin` | Full unrestricted access |
| **Financial Analyst** | `analyst` | `nexus-analyst` | Predictions, money flow, model evaluation |
| **Case Viewer** | `viewer` | `nexus-viewer` | Read-only observation |

---

## 4. End-to-End Demo Scenario

1. **Log in** as `investigator` (`nexus-demo`).
2. **Dashboard**: View high-level KPIs (Total Complaints, ₹ Fraud Volume, High-Risk Clusters, Active Alerts, Top-5 Hit Rate).
3. **Select Complaint** `C1001` (Victim lost ₹1,20,000 under Card Skimming / OTP Fraud).
4. **Click "Predict Cash-Out"**:
   - The live LightGBM model executes spatio-temporal inference in ~2 ms.
   - Outputs ranked candidate locations:
     - **Rank #1**: Andheri West Lokhandwala Hub → Risk **89/100** • Window: **14:00–18:00**
     - **Rank #2**: Bandra Kurla Complex Tech Zone → Risk **67/100** • Window: **14:00–18:00**
     - **Rank #3**: Kothrud Paud Road Corridor → Risk **18/100**
   - TreeSHAP explains top signals: syndicate affinity (+0.42), ATM density (+0.28).
5. **Inspect GIS Heatmap**: View Andheri West cluster pulsing red with monitored ATMs.
6. **Trace Money Flow**: Open Cytoscape graph to see `Victim` → `Mule L1 (ACC-SYN-MUM-01-L1-01)` → `Mule L2 (ACC-SYN-MUM-01-L2-01)` → `ATM-123 Cash-Out`.
7. **Review Alerts**: Notice auto-generated Critical Alert; change status to `Investigating`.
8. **Consult RAG Copilot**: Ask *"Why was this location ranked highly and what evidence supports it?"* — receives grounded answer with SHA-256 evidence citations.
9. **Inspect Model Evaluation**: Review authentic ROC-AUC (0.9286), PR-AUC (0.7586), and Top-5 Hit Rate (100.0%).

---

## 5. Automated Tests

Run the full pytest suite from the backend directory:
```powershell
Set-Location 'L:\NEXUS_working_prototype\backend'
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
All 16 unit, integration, and security tests pass.
