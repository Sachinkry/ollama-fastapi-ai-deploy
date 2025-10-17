
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.core.config import settings

client = TestClient(app)

# Get a valid key from the settings
VALID_API_KEY = list(settings.API_KEYS)[0]

def test_enqueue_generate_success(monkeypatch):
    """Test successful enqueue of a generation job."""
    # Mock the celery task's delay method
    mock_delay = MagicMock()
    mock_delay.return_value = MagicMock(id="test-job-123")
    monkeypatch.setattr("app.worker.generate_text_task.delay", mock_delay)

    payload = {
        "model": "qwen3:0.6b",
        "prompt": "Why is the sky blue?",
        "max_tokens": 100,
    }

    response = client.post(
        "/generate",
        headers={"x-api-key": VALID_API_KEY},
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {"job_id": "test-job-123", "status": "queued"}

    # Verify that the task was called correctly
    mock_delay.assert_called_once_with(
        payload["model"],
        payload["prompt"],
        payload["max_tokens"],
        0.7,  # temperature defaults to 0.7 in the pydantic model
    )

def test_enqueue_generate_no_api_key():
    """Test request without an API key."""
    response = client.post("/generate", json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid API key"}

def test_enqueue_generate_invalid_api_key():
    """Test request with an invalid API key."""
    response = client.post(
        "/generate",
        headers={"x-api-key": "invalid-key"},
        json={},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid API key"}
