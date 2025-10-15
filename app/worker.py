from app.core.celery_app import celery_app
from app.services.ollama_client import OllamaClient
import asyncio

@celery_app.task(bind=True, name="generate_text_task")
def generate_text_task(self, model: str, prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """Celery worker task: independent Ollama connection."""
    async def _run():
        ollama = OllamaClient()
        result = await ollama.generate_once(
            model=model,
            prompt=prompt,
            options={"num_predict": max_tokens, "temperature": temperature},
        )
        await ollama.close()
        return result

    return asyncio.run(_run())
