"""
Redis database cache - Automatic caching for database queries
"""
import hashlib
import json
from typing import Any, Dict, List, Optional, Callable
from .client import get_redis_client

class DatabaseCache:
    """Automatic database query caching"""

    def __init__(self, default_ttl: int = 300):
        self.redis_client = get_redis_client()
        self.default_ttl = default_ttl

    def _generate_cache_key(self, query_type: str, table: str, conditions: Dict[str, Any], extra: str = "") -> str:
        """Generate unique cache key for query"""
        # Create deterministic string from query parameters
        key_data = f"{query_type}:{table}:{json.dumps(conditions, sort_keys=True)}:{extra}"
        # Hash for consistent length
        return f"db_cache:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def cache_query_result(self, query_type: str, table: str, conditions: Dict[str, Any],
                                result: Any, ttl: Optional[int] = None) -> bool:
        """Cache database query result"""
        try:
            cache_key = self._generate_cache_key(query_type, table, conditions)
            result_json = json.dumps(result, default=str)
            await self.redis_client.setex(cache_key, ttl or self.default_ttl, result_json)
            return True
        except Exception as e:
            print(f"Database cache set error: {e}")
            return False

    async def get_cached_query(self, query_type: str, table: str, conditions: Dict[str, Any]) -> Optional[Any]:
        """Get cached database query result"""
        try:
            cache_key = self._generate_cache_key(query_type, table, conditions)
            cached_result = await self.redis_client.get(cache_key)

            if cached_result:
                return json.loads(cached_result)
            return None
        except Exception as e:
            print(f"Database cache get error: {e}")
            return None

    async def invalidate_table_cache(self, table: str) -> bool:
        """Invalidate all cache entries for a table"""
        try:
            # Use SCAN to find all keys matching pattern
            pattern = f"db_cache:*{table}*"
            keys = []

            cursor = 0
            while True:
                cursor, partial_keys = await self.redis_client.scan(cursor, match=pattern)
                keys.extend(partial_keys)
                if cursor == 0:
                    break

            if keys:
                await self.redis_client.delete(*keys)

            return True
        except Exception as e:
            print(f"Database cache invalidation error: {e}")
            return False

    async def cache_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Cache user profile data"""
        return await self.cache_query_result("select", "users", {"id": user_id}, profile_data)

    async def get_cached_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile"""
        return await self.get_cached_query("select", "users", {"id": user_id})

    async def cache_products_list(self, category: str, products: List[Dict[str, Any]]) -> bool:
        """Cache products list by category"""
        return await self.cache_query_result("select", "products", {"category": category}, products, ttl=600)

    async def get_cached_products_list(self, category: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached products list"""
        return await self.get_cached_query("select", "products", {"category": category})

# Global database cache instance
_db_cache = None

def get_database_cache() -> DatabaseCache:
    """Get global database cache instance"""
    global _db_cache
    if _db_cache is None:
        _db_cache = DatabaseCache()
    return _db_cache

async def cache_db_query(query_type: str, table: str, conditions: Dict[str, Any],
                        result: Any, ttl: Optional[int] = None) -> bool:
    """Cache database query result"""
    cache = get_database_cache()
    return await cache.cache_query_result(query_type, table, conditions, result, ttl)

async def get_cached_db_query(query_type: str, table: str, conditions: Dict[str, Any]) -> Optional[Any]:
    """Get cached database query result"""
    cache = get_database_cache()
    return await cache.get_cached_query(query_type, table, conditions)

async def invalidate_db_cache(table: str) -> bool:
    """Invalidate all cache for a table"""
    cache = get_database_cache()
    return await cache.invalidate_table_cache(table)
