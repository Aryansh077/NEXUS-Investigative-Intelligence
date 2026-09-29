from fastapi.testclient import TestClient
from app.main import app
from app.security.hashing import sha256_text, hash_password, verify_password
from app.security.rbac import has_permission

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "LightGBM" in data["model"]

def test_summary_kpis():
    res = client.get("/api/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["complaints"] >= 40
    assert data["atms"] >= 50
    assert data["transactions"] >= 100

def test_model_metrics_unbiased():
    res = client.get("/api/model/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["best_model"] == "LightGBM"
    lgbm = data["models"]["LightGBM"]
    assert lgbm["roc_auc"] > 0.85
    assert lgbm["top5_hit_rate"] >= 0.90
    assert lgbm["avg_inference_latency_ms"] < 20.0

def test_live_cashout_prediction():
    res = client.post(
        "/api/predictions/predict",
        json={"complaint_id": "C1001", "top_k": 3, "alert_threshold": 65.0}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["complaint_id"] == "C1001"
    assert len(data["predictions"]) == 3
    top_pred = data["predictions"][0]
    assert "risk_score" in top_pred
    assert 0.0 <= top_pred["risk_score"] <= 100.0
    assert "prediction_window" in top_pred
    assert len(top_pred["top_drivers"]) > 0

def test_money_flow_analysis():
    res = client.get("/api/financial/flow/C1001")
    assert res.status_code == 200
    data = res.json()
    assert data["victim_reported_loss"] > 0
    assert len(data["nodes"]) >= 3
    assert len(data["edges"]) >= 2
    types = [n["data"]["type"] for n in data["nodes"]]
    assert "VICTIM" in types

def test_grounded_rag_assistant():
    res = client.post(
        "/api/rag/ask",
        json={
            "case_id": "CASE-1021",
            "question": "What evidence records exist for this case?"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is True
    assert "SHA-256" in data["answer"]
    assert len(data["sources"]) > 0

def test_evidence_integrity_hashing():
    text = "Victim reported being defrauded under investment scam."
    h1 = sha256_text(text)
    h2 = sha256_text(text)
    assert h1 == h2
    assert len(h1) == 64
    assert h1 != sha256_text(text + " tampered")

def test_rbac_matrix():
    assert has_permission("admin", "any:operation") is True
    assert has_permission("investigator", "predictions:run") is True
    assert has_permission("analyst", "model:evaluate") is True
    assert has_permission("viewer", "cases:read") is True
    assert has_permission("viewer", "predictions:run") is False
