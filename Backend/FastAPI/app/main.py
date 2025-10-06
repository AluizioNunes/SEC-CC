from fastapi import FastAPI, HTTPException, Depends
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import os
import redis.asyncio as redis
import json
import time
from typing import Optional
import asyncio

app = FastAPI(title="SEC FastAPI", version="0.1.0")

# Redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

# Prometheus metrics
REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "path"])
REDIS_OPERATIONS = Counter("redis_operations_total", "Redis operations", ["operation", "status"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    method = request.method
    path = request.url.path
    with REQUEST_LATENCY.labels(method=method, path=path).time():
        response = await call_next(request)
    REQUEST_COUNTER.labels(method=method, path=path, status=str(response.status_code)).inc()
    return response

# Cache utilities
async def get_cache(key: str) -> Optional[str]:
    """Get value from Redis cache"""
    try:
        value = await redis_client.get(key)
        REDIS_OPERATIONS.labels(operation="get", status="success").inc()
        return value
    except Exception as e:
        REDIS_OPERATIONS.labels(operation="get", status="error").inc()
        logger.error(f"Redis get error: {e}")
        return None

async def set_cache(key: str, value: str, ttl: int = 300) -> bool:
    """Set value in Redis cache with TTL"""
    try:
        await redis_client.setex(key, ttl, value)
        REDIS_OPERATIONS.labels(operation="set", status="success").inc()
        return True
    except Exception as e:
        REDIS_OPERATIONS.labels(operation="set", status="error").inc()
        logger.error(f"Redis set error: {e}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete key from Redis cache"""
    try:
        await redis_client.delete(key)
        REDIS_OPERATIONS.labels(operation="delete", status="success").inc()
        return True
    except Exception as e:
        REDIS_OPERATIONS.labels(operation="delete", status="error").inc()
        logger.error(f"Redis delete error: {e}")
        return False

# Session management
async def create_session(user_id: str, data: dict) -> str:
    """Create user session"""
    session_id = f"session:{user_id}:{int(time.time())}"
    session_data = json.dumps(data)
    await redis_client.setex(session_id, 3600, session_data)  # 1 hour TTL
    return session_id

async def get_session(session_id: str) -> Optional[dict]:
    """Get session data"""
    session_data = await redis_client.get(session_id)
    if session_data:
        return json.loads(session_data)
    return None

async def delete_session(session_id: str) -> bool:
    """Delete session"""
    return await delete_cache(session_id)

# Queue operations
async def enqueue_job(queue_name: str, job_data: dict) -> bool:
    """Add job to queue"""
    try:
        job_json = json.dumps(job_data)
        await redis_client.lpush(f"queue:{queue_name}", job_json)
        REDIS_OPERATIONS.labels(operation="enqueue", status="success").inc()
        return True
    except Exception as e:
        REDIS_OPERATIONS.labels(operation="enqueue", status="error").inc()
        logger.error(f"Redis enqueue error: {e}")
        return False

async def dequeue_job(queue_name: str) -> Optional[dict]:
    """Get job from queue"""
    try:
        job_json = await redis_client.rpop(f"queue:{queue_name}")
        if job_json:
            REDIS_OPERATIONS.labels(operation="dequeue", status="success").inc()
            return json.loads(job_json)
        return None
    except Exception as e:
        REDIS_OPERATIONS.labels(operation="dequeue", status="error").inc()
        logger.error(f"Redis dequeue error: {e}")
        return None

# Rate limiting
async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60) -> bool:
    """Check rate limit for user"""
    try:
        key = f"ratelimit:{user_id}"
        current = await redis_client.get(key)

        if current is None:
            await redis_client.setex(key, window, "1")
            return True

        count = int(current)
        if count >= limit:
            return False

        await redis_client.incr(key)
        return True
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error

# API Routes
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

# Cache endpoints
@app.get("/cache/{key}")
async def get_cached_value(key: str):
    """Get cached value"""
    value = await get_cache(key)
    if value:
        return {"key": key, "value": value}
    raise HTTPException(status_code=404, detail="Key not found")

@app.post("/cache/{key}")
async def set_cached_value(key: str, value: str, ttl: int = 300):
    """Set cached value"""
    success = await set_cache(key, value, ttl)
    if success:
        return {"message": "Value cached successfully", "ttl": ttl}
    raise HTTPException(status_code=500, detail="Failed to cache value")

@app.delete("/cache/{key}")
async def delete_cached_value(key: str):
    """Delete cached value"""
    success = await delete_cache(key)
    if success:
        return {"message": "Value deleted from cache"}
    raise HTTPException(status_code=500, detail="Failed to delete value")

# Session endpoints
@app.post("/session/{user_id}")
async def create_user_session(user_id: str, data: dict):
    """Create user session"""
    session_id = await create_session(user_id, data)
    return {"session_id": session_id, "user_id": user_id}

@app.get("/session/{session_id}")
async def get_user_session(session_id: str):
    """Get session data"""
    session_data = await get_session(session_id)
    if session_data:
        return {"session_id": session_id, "data": session_data}
    raise HTTPException(status_code=404, detail="Session not found")

# Queue endpoints
@app.post("/queue/{queue_name}")
async def add_to_queue(queue_name: str, job_data: dict):
    """Add job to queue"""
    success = await enqueue_job(queue_name, job_data)
    if success:
        return {"message": "Job added to queue", "queue": queue_name}
    raise HTTPException(status_code=500, detail="Failed to add job to queue")

@app.get("/queue/{queue_name}")
async def get_from_queue(queue_name: str):
    """Get job from queue"""
    job = await dequeue_job(queue_name)
    if job:
        return {"job": job, "queue": queue_name}
    raise HTTPException(status_code=404, detail="No jobs in queue")

# Rate limiting endpoint
@app.get("/rate-limit/{user_id}")
async def check_user_rate_limit(user_id: str):
    """Check rate limit for user"""
    allowed = await check_rate_limit(user_id)
    return {"user_id": user_id, "allowed": allowed}

# Statistics endpoint
@app.get("/redis/stats")
async def redis_statistics():
    """Get Redis statistics"""
    try:
        info = await redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "uptime_days": info.get("uptime_in_days", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis info error: {e}")

# Background task for queue processing
async def process_queues():
    """Background task to process queues"""
    while True:
        try:
            # Process different queues
            for queue in ["email", "reports", "cleanup"]:
                job = await dequeue_job(queue)
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
