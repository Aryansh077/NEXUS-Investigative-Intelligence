from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_demo_login():
    response = client.post(
        "/api/auth/login",
        json={"username": "investigator", "password": "nexus-demo"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "investigator"


def test_invalid_login_is_rejected():
    response = client.post(
        "/api/auth/login",
        json={"username": "investigator", "password": "wrong"},
    )
    assert response.status_code == 401