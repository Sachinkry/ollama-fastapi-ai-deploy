import os

class Settings:
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    # Control-plane limits
    CONCURRENCY_LIMIT: int = int(os.getenv("CONCURRENCY_LIMIT", "4"))
    REQUEST_TIMEOUT_S: float = float(os.getenv("REQUEST_TIMEOUT_S", "60"))
    # super basic API keys (move to Redis/DB later)
    API_KEYS: set[str] = set(os.getenv("API_KEYS", "dev-key-123").split(","))

settings = Settings()
