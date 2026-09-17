from collections.abc import Mapping

from .anomaly_detection import detect_anomalies


def evaluate_unsupervised_case(
    entity_ids: list[str], relationships: list[Mapping[str, object]]
) -> dict[str, object]:
    """Report operational screening counts, not unsupported accuracy metrics."""
    anomalies = detect_anomalies(entity_ids, relationships)
    return {
        "entity_count": len(entity_ids),
        "relationship_count": len(relationships),
        "anomaly_count": len(anomalies),
        "evaluation_type": "unsupervised_runtime_screening",
        "note": "No labeled ground truth is available for synthetic demo data.",
    }