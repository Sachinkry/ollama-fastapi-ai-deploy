# app/api/routes_models.py
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("")  
async def list_models(request: Request):
    try:
        client = request.app.state.ollama  # ✅ use app.state
        models = await client.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
