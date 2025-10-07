"""
Redis Client Module
Centralized Redis client management for the SEC application.
"""
import os
import redis.asyncio as redis
from typing import Optional


# Redis client singleton
_redis_client = None


def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            max_connections=20
        )
    return _redis_client


async def close_redis_connection():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        client = get_redis_client()
        await client.ping()
        return True
    except Exception:
        return False