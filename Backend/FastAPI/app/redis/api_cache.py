"""
Advanced API Response Caching
Intelligent caching with multiple strategies and automatic invalidation
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any, Callable, List
from functools import wraps
import asyncio
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .client import get_redis_client


class APICacheManager:
    """Advanced API Response Cache Manager"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_prefix = "api_response_cache"
        self.default_ttl = 300  # 5 minutes

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }

    def _generate_cache_key(self, request: Request, user_id: str = None, params: dict = None) -> str:
        """Generate unique cache key for request"""
        key_data = {
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "user_id": user_id,
            "params": params or {}
        }

        # Remove sensitive data
        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_key}"

    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response"""
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                cache_info = json.loads(cached_data)
                self.stats["hits"] += 1

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) > cache_info.get("ttl", self.default_ttl):
                    await self.redis_client.delete(cache_key)
                    self.stats["misses"] += 1
                    return None

                return cache_info
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Cache read error: {e}")
            return None

    async def set_cached_response(
        self,
        cache_key: str,
        response_data: Dict[str, Any],
        ttl: int = None,
        tags: List[str] = None,
        headers: Dict[str, str] = None
    ) -> bool:
        """Store response in cache with metadata"""
        try:
            cache_data = {
                "data": response_data,
                "cached_at": time.time(),
                "ttl": ttl or self.default_ttl,
                "tags": tags or [],
                "headers": headers or {}
            }

            await self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl,
                json.dumps(cache_data, default=str)
            )

            self.stats["sets"] += 1
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Cache write error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        if not tags:
            return 0

        try:
            # Get all cache keys
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            invalidated = 0
            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    if any(tag in cache_info.get("tags", []) for tag in tags):
                        await self.redis_client.delete(key)
                        invalidated += 1

            return invalidated
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0

    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries by pattern"""
        try:
            keys = await self.redis_client.keys(f"{self.cache_prefix}:{pattern}")
            if keys:
                await self.redis_client.delete(*keys)
            return len(keys)
        except Exception as e:
            print(f"Cache pattern invalidation error: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "errors": self.stats["errors"],
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": "estimated"  # Would need Redis INFO command
        }


# Global cache manager instance
api_cache_manager = APICacheManager()


def cache_response(
    ttl: int = 300,
    tags: List[str] = None,
    vary_by_user: bool = False,
    condition: Callable = None,
    include_headers: bool = False
):
    """
    Decorator for caching API responses

    Args:
        ttl: Time to live in seconds
        tags: Tags for cache invalidation
        vary_by_user: Whether to vary cache by user ID
        condition: Optional function to determine if response should be cached
        include_headers: Whether to cache response headers
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args (FastAPI dependency injection)
            request = None
            for arg in args:
                if hasattr(arg, 'method'):  # Likely a Request object
                    request = arg
                    break

            if not request:
                # Try to find request in kwargs
                request = kwargs.get('request')

            if not request:
                # No request found, execute without caching
                return await func(*args, **kwargs)

            # Check condition if provided
            if condition and not condition(request):
                return await func(*args, **kwargs)

            # Generate cache key
            user_id = None
            if vary_by_user:
                # Try to extract user_id from various sources
                user_id = getattr(request.state, 'user_id', None) or \
                         request.headers.get('X-User-ID') or \
                         request.query_params.get('user_id')

            cache_key = api_cache_manager._generate_cache_key(request, user_id)

            # Try to get from cache
            cached_response = await api_cache_manager.get_cached_response(cache_key)
            if cached_response:
                # Return cached response
                response_data = cached_response["data"]
                response_headers = cached_response.get("headers", {})

                response = JSONResponse(
                    content=response_data,
                    headers={"X-Cache": "HIT", **response_headers}
                )
                return response

            # Execute function and cache result
            result = await func(*args, **kwargs)

            # Extract response data (handle both dict and Response objects)
            response_data = result
            response_headers = {}

            if hasattr(result, 'body') and hasattr(result, 'headers'):
                # It's a Response object
                if hasattr(result, 'media_type') and 'json' in result.media_type:
                    try:
                        response_data = json.loads(result.body)
                    except:
                        response_data = {"message": "Response cached"}
                else:
                    response_data = {"message": "Non-JSON response cached"}

                if include_headers:
                    response_headers = dict(result.headers)

            # Cache the response
            await api_cache_manager.set_cached_response(
                cache_key,
                response_data,
                ttl,
                tags,
                response_headers
            )

            # Add cache header to response if it's a Response object
            if hasattr(result, 'headers'):
                result.headers["X-Cache"] = "MISS"

            return result

        return wrapper
    return decorator


async def invalidate_cache_by_tags(tags: List[str]) -> int:
    """Invalidate cache by tags"""
    return await api_cache_manager.invalidate_by_tags(tags)


async def invalidate_cache_by_pattern(pattern: str) -> int:
    """Invalidate cache by pattern"""
    return await api_cache_manager.invalidate_by_pattern(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return api_cache_manager.get_cache_stats()
