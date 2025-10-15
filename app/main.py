# app/main.py

from fastapi import FastAPI, Request, Response
# --- FIX: Import CORSMiddleware ---
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio, time
from app.api import routes_generate, routes_models, routes_status
from app.core.config import settings
from app.core.logger import logger
from app.core.metrics import render_metrics, LATENCY, REQUESTS, ERRORS
from app.services.ollama_client import ollama

app = FastAPI(title="Prodify Gateway", version="3.0.0")

# --- FIX: Add CORS Middleware ---
# This must be placed before you include your routers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"], # The origins your frontend is running on
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


# Concurrency limit (control-plane)
sem = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # health + metrics are public
        if request.url.path in ("/healthz", "/readyz", "/metrics", "/static/index.html"):
            return await call_next(request)

        # latency metrics wrapper
        model = "unknown"
        if request.headers.get("content-type") == "application/json":
            try:
                body = await request.json()
                model = body.get("model", "unknown")
                # Restore the body for the actual endpoint
                async def receive():
                    return {"type": "http.request", "body": await request.body()}
                request = Request(request.scope, receive)
            except:
                pass # ignore json parsing errors

        route = request.url.path
        start = time.perf_counter()
        resp = None
        try:
            async with sem:
                resp = await call_next(request)
            return resp
        except Exception:
            ERRORS.labels(route=route, model=model).inc()
            raise
        finally:
            if resp: # only record latency/requests on success
                LATENCY.labels(route=route, model=model).observe(time.perf_counter() - start)
                REQUESTS.labels(route=route, model=model).inc()


app.add_middleware(MetricsMiddleware)

# Routers
app.include_router(routes_models.router, prefix="/models", tags=["Models"])
app.include_router(routes_generate.router, prefix="/generate", tags=["Generate"])

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Gateway starting...")
    await ollama.connect()
    try:
        models = await ollama.list_models()
        logger.info(f"✅ Ollama reachable. Models available: {models}")
    except Exception as e:
        logger.error(f"❌ Ollama not reachable on startup: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🌙 Gateway shutting down.")
    await ollama.close()

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/readyz")
async def readyz():
    try:
        models = await ollama.list_models()
        return {"ready": True, "models": len(models)}
    except Exception as e:
        return {"ready": False, "error": str(e)}

@app.get("/metrics")
async def metrics():
    body, ctype = render_metrics()
    return Response(content=body, media_type=ctype)

app.include_router(routes_status.router, prefix="/status", tags=["Status"])
