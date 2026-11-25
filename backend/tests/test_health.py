from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok_and_low_rss() -> None:
    """Verify /api/v1/health responds 200 OK and stays within memory budget."""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert isinstance(payload["rss_mb"], float)
    assert payload["rss_mb"] < 150.0
