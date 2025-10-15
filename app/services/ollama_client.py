import httpx
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        """Initialize a self-contained Ollama HTTP client."""
        self.base_url = base_url
        # immediately create an AsyncClient — no .connect() required
        self.client = httpx.AsyncClient(timeout=120)

    async def list_models(self):
        """Fetch available Ollama models."""
        try:
            r = await self.client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error fetching Ollama models: {e}")
            return []

    async def generate_once(self, model: str, prompt: str, options: dict = None):
        """Stream inference output and combine into final text."""
        options = options or {}
        payload = {
            "model": model,
            "prompt": prompt,
            "options": options,
            "stream": True
        }

        full_text = ""
        try:
            async with self.client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "response" in data and data["response"]:
                            full_text += data["response"]
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error during Ollama generation: {e}")
            raise
        return {"model": model, "text": full_text.strip()}

    async def close(self):
        """Cleanly close the HTTP connection."""
        await self.client.aclose()
