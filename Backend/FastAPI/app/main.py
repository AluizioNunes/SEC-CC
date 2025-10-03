from fastapi import FastAPI
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import os

app = FastAPI(title="SEC FastAPI", version="0.1.0")

REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "path"]) 

@app.middleware("http")
async def metrics_middleware(request, call_next):
    method = request.method
    path = request.url.path
    with REQUEST_LATENCY.labels(method=method, path=path).time():
        response = await call_next(request)
    REQUEST_COUNTER.labels(method=method, path=path, status=str(response.status_code)).inc()
    return response

@app.get("/health")
async def health():
    logger.info("FastAPI health check")
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/python/info")
async def info():
    return {
        "service": "fastapi",
        "postgres_url": os.getenv("POSTGRES_URL", "postgres://sec:secpass@postgres:5432/secdb"),
        "mongodb_url": os.getenv("MONGODB_URL", "mongodb://mongodb:27017/secmongo"),
        "redis_url": os.getenv("REDIS_URL", "redis://redis:6379/0"),
    }
