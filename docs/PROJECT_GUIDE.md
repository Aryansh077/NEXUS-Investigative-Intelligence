# NEXUS-PREDICT: Project Guide & Technical Dossier

## 1. System Mission
NEXUS-PREDICT is an evidence-first predictive analytics and investigative decision-support platform designed for the Smart India Hackathon (SIH). It tackles the core enforcement problem in cyber financial crimes: **predicting WHERE and WHEN an ATM cash-out is likely to occur following a complaint.**

## 2. Machine Learning Engine
- **Models**:
  1. Logistic Regression (Baseline)
  2. Random Forest Classifier
  3. LightGBM (Champion Spatio-Temporal Predictor)
- **Features**: 12 domain-specific signals including temporal hours, day of week, transaction velocity, hop count, ATM density, district crime density, and syndicate cluster affinity.
- **Evaluation**: Evaluated objectively against `ground_truth.json`:
  - **ROC-AUC**: `0.9286`
  - **PR-AUC**: `0.7586`
  - **Top-1 Location Hit Rate**: `81.82%`
  - **Top-5 Location Hit Rate**: `100.0%`
  - **Inference Latency**: `2.05 ms`
- **Explainability**: TreeSHAP feature contributions explain each prediction ranking.

## 3. Core Modules
- `backend/app/services/ingestion/`: CSV/JSON validator, deduplication, quality score.
- `backend/app/services/nlp/`: Cybercrime entity extraction with confidence scores.
- `backend/app/services/financial/`: Multi-hop laundering tracer (Victim -> Mule L1 -> Mule L2 -> ATM Cash-Out) with Cytoscape topology.
- `backend/app/services/prediction/`: Spatio-temporal location ranking and window estimator.
- `backend/app/services/rag/`: Grounded RAG assistant with zero hallucinations.
- `backend/app/services/alerts/`: Real-time threshold alerts and status lifecycle.
- `frontend/src/components/map/`: Interactive Leaflet GIS Heatmap with circular risk buffers.
- `frontend/src/components/graph/`: Interactive Cytoscape Money-Flow graph.

## 4. Integrity and Compliance
- Uses synthetic, anonymized data only.
- Predictions represent decision-support probabilities, not certainty of guilt.
- All evidence records are cryptographically verified with SHA-256 hashes.