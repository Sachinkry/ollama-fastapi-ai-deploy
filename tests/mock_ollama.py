from fastapi import FastAPI, Response
import uvicorn
import json
import time
import asyncio

app = FastAPI()

@app.get("/api/tags")
async def list_models():
    return {"models": [{"name": "mock-model:latest"}]}

@app.post("/api/generate")
async def generate():
    async def generate_stream():
        for i in range(5):
            response = {
                "model": "mock-model:latest",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
                "response": f"Mock response chunk {i+1}. ",
                "done": False
            }
            yield json.dumps(response) + "\n"
            await asyncio.sleep(0.1)
        
        final_response = {
            "model": "mock-model:latest",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "response": "",
            "done": True
        }
        yield json.dumps(final_response) + "\n"

    return Response(generate_stream(), media_type="application/x-ndjson")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11434)

