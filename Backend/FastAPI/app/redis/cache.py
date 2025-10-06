"""
Redis cache operations
"""
from typing import Optional
from .client import get_redis_client

async def get_cache(key: str) -> Optional[str]:
    """Get value from Redis cache"""
    redis_client = get_redis_client()
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"Redis get error: {e}")
        return None

async def set_cache(key: str, value: str, ttl: int = 300) -> bool:
    """Set value in Redis cache with TTL"""
    redis_client = get_redis_client()
    try:
        await redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete key from Redis cache"""
    redis_client = get_redis_client()
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis delete error: {e}")
        return False

async def exists_cache(key: str) -> bool:
    """Check if key exists in cache"""
    redis_client = get_redis_client()
    try:
        return await redis_client.exists(key) > 0
    except Exception as e:
        print(f"Redis exists error: {e}")
        return False
