# app/services/ollama_client.py

import httpx
from app.core.config import settings
import logging

logger = logging.getLogger("prodify")

class OllamaClient:
    def __init__(self):
        self.base = settings.OLLAMA_HOST
        # --- FIX: Initialize client to None. It will be created on app startup. ---
        self.client: httpx.AsyncClient | None = None

    # --- FIX: Add a connect method to be called from the startup event. ---
    async def connect(self):
        """Create the AsyncClient instance."""
        if not self.client:
            logger.info("OllamaClient connecting...")
            self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_S)

    async def close(self):
        """Close the AsyncClient instance."""
        if self.client:
            logger.info("OllamaClient closing...")
            await self.client.aclose()
            self.client = None

    def _ensure_client(self):
        """Ensure the client has been initialized."""
        if not self.client:
            raise RuntimeError("Ollama client not initialized. Call connect() first.")

    async def list_models(self) -> list[str]:
        self._ensure_client()
        r = await self.client.get(f"{self.base}/api/tags")
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]

    async def generate_once(self, model: str, prompt: str, options: dict | None = None):
        """Non-streaming, one-shot generation."""
        self._ensure_client()
        payload = {"model": model, "prompt": prompt, "stream": False}
        if options:
            payload["options"] = options
        r = await self.client.post(f"{self.base}/api/generate", json=payload)
        r.raise_for_status()
        return r.json()

    async def stream_generate(self, model: str, prompt: str, options: dict | None = None):
        """Streaming version: yields NDJSON lines from Ollama."""
        self._ensure_client()
        payload = {"model": model, "prompt": prompt, "stream": True}
        if options:
            payload["options"] = options

        async with self.client.stream("POST", f"{self.base}/api/generate", json=payload) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line:
                    continue
                yield line

# Singleton
ollama = OllamaClient()