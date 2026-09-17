from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURE_COLUMNS = [
    "interaction_count",
    "unique_contacts",
    "night_interaction_count",
    "mean_confidence",
]


def _features(entity_ids: list[str], relationships: list[Mapping[str, object]]) -> pd.DataFrame:
    values = {
        entity_id: {column: 0.0 for column in FEATURE_COLUMNS}
        for entity_id in entity_ids
    }
    contacts = {entity_id: set() for entity_id in entity_ids}
    for relationship in relationships:
        source = str(relationship.get("source_id", ""))
        if source not in values:
            continue
        values[source]["interaction_count"] += 1
        target = str(relationship.get("target_id", ""))
        if target:
            contacts[source].add(target)
        try:
            hour = datetime.fromisoformat(
                str(relationship.get("timestamp", "")).replace("Z", "+00:00")
            ).hour
            if hour < 6 or hour >= 22:
                values[source]["night_interaction_count"] += 1
        except (TypeError, ValueError):
            pass
        try:
            values[source]["mean_confidence"] += float(relationship.get("confidence") or 0.0)
        except (TypeError, ValueError):
            pass
    for entity_id in entity_ids:
        count = values[entity_id]["interaction_count"]
        values[entity_id]["unique_contacts"] = float(len(contacts[entity_id]))
        values[entity_id]["mean_confidence"] = (
            values[entity_id]["mean_confidence"] / count if count else 0.0
        )
    return pd.DataFrame.from_dict(values, orient="index")[FEATURE_COLUMNS]


def detect_anomalies(entity_ids: list[str], relationships: list[Mapping[str, object]]):
    features = _features(entity_ids, relationships)
    if len(features) < 2:
        return []
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    predictions = model.fit_predict(features)
    scores = model.decision_function(features)
    baseline = features.median()
    results = []
    labels = {
        "interaction_count": "unusually high communication volume",
        "unique_contacts": "unusually high number of unique contacts",
        "night_interaction_count": "unusual late-night activity",
    }
    for index, entity_id in enumerate(features.index):
        if predictions[index] != -1:
            continue
        row = features.loc[entity_id]
        reasons = [
            label for feature, label in labels.items()
            if row[feature] > baseline[feature] * 1.5 and row[feature] > baseline[feature] + 1
        ] or ["feature combination differs from the case baseline"]
        score = max(0.0, min(1.0, 0.5 - float(scores[index])))
        results.append({
            "entity_id": entity_id,
            "score": round(score, 3),
            "severity": "high" if score >= 0.65 else "medium",
            "reasons": reasons,
            "features": {column: float(row[column]) for column in FEATURE_COLUMNS},
        })
    return sorted(results, key=lambda item: item["score"], reverse=True)