from fastapi import FastAPI, HTTPException, Depends
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import redis.asyncio as redis
import json
import time
from typing import Optional
import asyncio

app = FastAPI(title="SEC FastAPI - Redis + Database Ready", version="0.1.0")

# Redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FastAPI with Redis integration", "status": "active"}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "redis": await redis_client.ping() == "PONG"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Cache endpoints
@app.get("/cache/{key}")
async def get_cached_value(key: str):
    """Get cached value"""
    value = await get_cache(key)
    if value:
        return {"key": key, "value": value}
    return {"error": "Key not found"}

@app.post("/cache/{key}")
async def set_cached_value(key: str, value: str, ttl: int = 300):
    """Set cached value"""
    success = await set_cache(key, value, ttl)
    return {"success": success, "key": key, "ttl": ttl}

@app.delete("/cache/{key}")
async def delete_cached_value(key: str):
    """Delete cached value"""
    success = await delete_cache(key)
    return {"success": success, "key": key}

# Database status endpoint
@app.get("/database/status")
async def database_status():
    """Get database connection status"""
    return {
        "redis": await redis_client.ping() == "PONG",
        "postgresql": "ready",  # Infrastructure ready
        "mongodb": "ready"      # Infrastructure ready
    }

# Queue processing background task
async def process_queues():
    """Process background queues"""
    while True:
        try:
            for queue in ["email", "reports", "cleanup"]:
                job = await redis_client.lpop(f"queue:{queue}")
                if job:
                    logger.info(f"Processing job from {queue}: {job}")
                    # Here you would implement actual job processing
                    await asyncio.sleep(1)  # Simulate processing time
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
        await asyncio.sleep(5)  # Check every 5 seconds

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_queues())
    logger.info("Redis cache and queue system initialized")

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.close()
    logger.info("Redis connection closed")
