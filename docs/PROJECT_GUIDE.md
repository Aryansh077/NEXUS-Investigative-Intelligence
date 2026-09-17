
## ML status

The anomaly API uses a deterministic `IsolationForest` fitted at request time
on features derived from the current case relationships: interaction count,
unique contacts, late-night interactions, and mean source confidence. It is not
a pretrained or proprietary model. The synthetic demo has no labeled ground
truth, so the project does not report accuracy, precision, recall, or F1.
# NEXUS Project Guide

NEXUS is an evidence-first investigative analytics prototype. It connects
synthetic records, exposes relationships and unusual activity, and keeps source
records visible for investigator review.

The system does not identify criminals or determine guilt. Every anomaly and
inferred relationship is a reviewable lead with confidence and provenance where
available.

Main ownership areas are grouped under `backend/app`, `frontend`, `ml`, and
`neo4j`. Keep API changes synchronized with the frontend and add focused tests
for new analytical behavior.