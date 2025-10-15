from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import require_api_key
from app.worker import generate_text_task

router = APIRouter()

class GenerateRequest(BaseModel):
    model: str = "qwen3:0.6b"
    prompt: str
    max_tokens: int | None = None
    temperature: float | None = 0.7
    top_p: float | None = 0.9
    stream: bool = False

@router.post("", dependencies=[Depends(require_api_key)])
async def enqueue_generate(req: GenerateRequest):
    """Enqueue text generation job"""
    task = generate_text_task.delay(req.model, req.prompt, req.max_tokens, req.temperature)
    return {"job_id": task.id, "status": "queued"}

# @router.post("/", dependencies=[Depends(require_api_key)])
# async def generate(req: GenerateRequest):
#     options = {}
#     if req.max_tokens is not None: options["num_predict"] = req.max_tokens
#     if req.temperature is not None: options["temperature"] = req.temperature
#     if req.top_p is not None: options["top_p"] = req.top_p

#     if not req.stream:
#         try:
#             data = await ollama.generate_once(req.model, req.prompt, options)
#             return JSONResponse(data)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))

#     async def gen():
#         try:
#             async for line in ollama.stream_generate(req.model, req.prompt, options):
#                 yield line + "\n"
#         except Exception as e:
#             yield json.dumps({"error": str(e)}) + "\n"

#     return StreamingResponse(gen(), media_type="application/x-ndjson")
