
import pytest

from fastapi.testclient import TestClient

import httpx



from app.main import app





def test_list_models_success(monkeypatch):

    """Test successful listing of models by monkeypatching the client method."""



    async def mock_list_models(*args, **kwargs):

        return ["qwen3:0.6b", "mistral:latest"]



    monkeypatch.setattr("app.services.ollama_client.OllamaClient.list_models", mock_list_models)



    with TestClient(app) as client:

        response = client.get("/models")



    assert response.status_code == 200

    assert response.json() == {"models": ["qwen3:0.6b", "mistral:latest"]}





def test_list_models_ollama_error(monkeypatch):

    """Test an error case by having the monkeypatched method raise an exception."""



    async def mock_list_models_error(*args, **kwargs):

        raise httpx.RequestError("Mocked network error")



    monkeypatch.setattr("app.services.ollama_client.OllamaClient.list_models", mock_list_models_error)



    with TestClient(app) as client:

        response = client.get("/models")



    assert response.status_code == 500

    assert "Mocked network error" in response.json()["detail"]
