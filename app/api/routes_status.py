from fastapi import APIRouter, HTTPException
from app.core.celery_app import celery_app

router = APIRouter()

@router.get("/{task_id}")
def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "pending"}
    elif task_result.state == "STARTED":
        return {"status": "running"}
    elif task_result.state == "FAILURE":
        return {"status": "failed", "error": str(task_result.info)}
    elif task_result.state == "SUCCESS":
        return {"status": "completed", "result": task_result.result}
    else:
        raise HTTPException(status_code=400, detail="Unknown state")
