
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    """Test the health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
