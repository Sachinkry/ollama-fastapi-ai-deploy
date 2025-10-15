from fastapi import Header, HTTPException, status
from app.core.config import settings

def require_api_key(x_api_key: str | None = Header(None)):
    if not x_api_key or x_api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )
