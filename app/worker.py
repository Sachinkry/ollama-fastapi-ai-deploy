from app.core.celery_app import celery_app
from app.services.ollama_client import OllamaClient
import asyncio
from app.core.logger import logger
import time

@celery_app.task(bind=True, name="generate_text_task")
def generate_text_task(self, model: str, prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """Celery worker task: independent Ollama connection."""
    async def _run():
        ollama = OllamaClient()
        # self.update_state(state="STARTED", meta={"progress": 0})
        logger.info(f"[{self.request.id}] Starting text generation at {time.time()}")
        result = await ollama.generate_once(
            model=model,
            prompt=prompt,
            options={"num_predict": max_tokens, "temperature": temperature},
        )
        logger.info(f"[{self.request.id}] Finished text generation at {time.time()}")
        await ollama.close()
        return result

    return asyncio.run(_run())
