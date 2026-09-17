from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime

import pandas as pd

FEATURE_COLUMNS = [
    "interaction_count",
    "unique_contacts",
    "night_interaction_count",
    "mean_confidence",
]


def _hour(value: object) -> int | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).hour
    except ValueError:
        return None


def build_entity_features(
    entity_ids: Iterable[str], relationships: Iterable[Mapping[str, object]]
) -> pd.DataFrame:
    features = {
        entity_id: {
            "interaction_count": 0,
            "unique_contacts": set(),
            "night_interaction_count": 0,
            "confidence_total": 0.0,
        }
        for entity_id in entity_ids
    }
    for relationship in relationships:
        source = str(relationship.get("source_id", ""))
        if source not in features:
            continue
        item = features[source]
        item["interaction_count"] += 1
        target = str(relationship.get("target_id", ""))
        if target:
            item["unique_contacts"].add(target)
        hour = _hour(relationship.get("timestamp"))
        if hour is not None and (hour < 6 or hour >= 22):
            item["night_interaction_count"] += 1
        try:
            item["confidence_total"] += float(relationship.get("confidence") or 0.0)
        except (TypeError, ValueError):
            pass
    rows = []
    for entity_id, item in features.items():
        count = item["interaction_count"]
        rows.append(
            {
                "entity_id": entity_id,
                "interaction_count": count,
                "unique_contacts": len(item["unique_contacts"]),
                "night_interaction_count": item["night_interaction_count"],
                "mean_confidence": round(item["confidence_total"] / count, 4)
                if count
                else 0.0,
            }
        )
    return pd.DataFrame(rows).set_index("entity_id")[FEATURE_COLUMNS]