# app/api/routes_status.py
from fastapi import APIRouter
from celery.result import AsyncResult
from app.worker import celery_app

router = APIRouter()

@router.get("/{job_id}")
async def get_status(job_id: str):
    """Return Celery job status and result."""
    result = AsyncResult(job_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "queued"}
    elif result.state == "STARTED":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        return {
            "status": "completed",
            "result": result.result,  # {'model': '...', 'text': '...'}
        }
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": result.state.lower()}
