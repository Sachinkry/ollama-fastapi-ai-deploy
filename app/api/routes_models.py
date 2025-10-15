from fastapi import APIRouter, HTTPException
from app.services.ollama_client import ollama

router = APIRouter()

@router.get("/")
async def list_models():
    try:
        models = await ollama.list_models()
        print("✅ Returning models:", models)
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
