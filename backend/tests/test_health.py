from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_identifies_synthetic_mode():
    response = client.get("/")
    assert response.status_code == 200
    if response.headers.get("content-type", "").startswith("application/json"):
        assert response.json()["data_mode"] == "synthetic"
    else:
        assert "<div id=\"root\"></div>" in response.text


def test_frontend_origins_include_dev_ports():
    from app.config import FRONTEND_ORIGINS

    assert "http://localhost:5173" in FRONTEND_ORIGINS
    assert "http://localhost:5174" in FRONTEND_ORIGINS