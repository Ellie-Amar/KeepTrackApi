from fastapi.testclient import TestClient
from app.main import app


def test_healthcheck_returns_ok():
    """simple sync test of healthcheck"""
    client = TestClient(app)
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
