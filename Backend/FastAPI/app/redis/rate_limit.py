"""
Redis rate limiting operations
"""
from .client import get_redis_client

async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60) -> bool:
    """Check rate limit for user"""
    redis_client = get_redis_client()
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
        print(f"Rate limit check error: {e}")
        return True  # Allow on error

async def get_rate_limit_status(user_id: str) -> dict:
    """Get rate limit status for user"""
    redis_client = get_redis_client()
    try:
        key = f"ratelimit:{user_id}"
        current = await redis_client.get(key)
        ttl = await redis_client.ttl(key)

        return {
            "user_id": user_id,
            "current_count": int(current) if current else 0,
            "ttl_seconds": ttl,
            "limit": 100,
            "window_seconds": 60
        }
    except Exception as e:
        print(f"Rate limit status error: {e}")
        return {"user_id": user_id, "error": str(e)}

async def reset_rate_limit(user_id: str) -> bool:
    """Reset rate limit for user"""
    redis_client = get_redis_client()
    try:
        key = f"ratelimit:{user_id}"
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Rate limit reset error: {e}")
        return False
