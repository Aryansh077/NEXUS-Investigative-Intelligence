from app.services.anomaly.model import detect_anomalies


def test_isolation_forest_output_is_deterministic_and_explainable():
    relationships = [
        {"source_id": "P1", "target_id": "P2", "timestamp": "2026-05-01T23:00", "confidence": 0.9},
        {"source_id": "P1", "target_id": "P3", "timestamp": "2026-05-02T23:00", "confidence": 0.9},
        {"source_id": "P1", "target_id": "P4", "timestamp": "2026-05-03T23:00", "confidence": 0.9},
        {"source_id": "P2", "target_id": "P3", "timestamp": "2026-05-03T10:00", "confidence": 0.9},
    ]
    first = detect_anomalies(["P1", "P2", "P3", "P4"], relationships)
    second = detect_anomalies(["P1", "P2", "P3", "P4"], relationships)
    assert first == second
    assert first
    assert first[0]["reasons"]