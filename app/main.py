# app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio, time
from app.api import routes_generate, routes_models, routes_status
from app.core.config import settings
from app.core.logger import logger
from app.core.metrics import render_metrics, LATENCY, REQUESTS, ERRORS
from app.services.ollama_client import OllamaClient  # ✅ use the class

app = FastAPI(title="Prodify Gateway", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sem = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/healthz", "/readyz", "/metrics", "/static/index.html"):
            return await call_next(request)

        model = "unknown"
        if request.headers.get("content-type") == "application/json":
            try:
                body_bytes = await request.body()
                body = body_bytes.decode("utf-8")
                # avoid consuming body: rebuild scope receive
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request = Request(request.scope, receive)
                import json
                model = json.loads(body).get("model", "unknown")
            except:
                pass

        route = request.url.path
        start = time.perf_counter()
        resp = None
        try:
            async with sem:
                resp = await call_next(request)
            return resp
        finally:
            if resp is not None:
                LATENCY.labels(route=route, model=model).observe(time.perf_counter() - start)
                REQUESTS.labels(route=route, model=model).inc()

app.add_middleware(MetricsMiddleware)

# Routers
app.include_router(routes_models.router, prefix="/models", tags=["Models"])
app.include_router(routes_generate.router, prefix="/generate", tags=["Generate"])
app.include_router(routes_status.router, prefix="/status", tags=["Status"])

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Gateway starting...")
    # ✅ create a client for the API process and keep it in app.state
    app.state.ollama = OllamaClient()
    try:
        models = await app.state.ollama.list_models()
        logger.info(f"✅ Ollama reachable. Models available: {models}")
    except Exception as e:
        logger.error(f"❌ Ollama not reachable on startup: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🌙 Gateway shutting down.")
    if hasattr(app.state, "ollama"):
        await app.state.ollama.close()

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/readyz")
async def readyz():
    try:
        models = await app.state.ollama.list_models()  # ✅ use app.state
        return {"ready": True, "models": len(models)}
    except Exception as e:
        return {"ready": False, "error": str(e)}

@app.get("/metrics")
async def metrics():
    body, ctype = render_metrics()
    return Response(content=body, media_type=ctype)
