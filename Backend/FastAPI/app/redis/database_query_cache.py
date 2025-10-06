"""
Database Query Caching - Performance Optimization
Intelligent caching of database queries with automatic invalidation
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any, List, Callable, Union
import asyncio

from .client import get_redis_client


class DatabaseQueryCache:
    """Advanced database query caching with intelligent invalidation"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_prefix = "db_query_cache"
        self.default_ttl = 300  # 5 minutes

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
            "errors": 0
        }

    def _generate_query_key(self, database: str, query_hash: str, params: Dict = None) -> str:
        """Generate unique cache key for database query"""
        key_data = {
            "database": database,
            "query_hash": query_hash,
            "params": params or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_key}"

    def _hash_query(self, query: str) -> str:
        """Generate hash for query string"""
        return hashlib.md5(query.encode()).hexdigest()

    async def get_cached_query(
        self,
        database: str,
        query: str,
        params: Dict = None
    ) -> Optional[Any]:
        """Retrieve cached query result"""
        try:
            query_hash = self._hash_query(query)
            cache_key = self._generate_query_key(database, query_hash, params)

            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                cache_info = json.loads(cached_data)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) > cache_info.get("ttl", self.default_ttl):
                    await self.redis_client.delete(cache_key)
                    self.stats["misses"] += 1
                    return None

                self.stats["hits"] += 1
                return cache_info["result"]
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Query cache read error: {e}")
            return None

    async def set_cached_query(
        self,
        database: str,
        query: str,
        params: Dict,
        result: Any,
        ttl: int = None,
        table_dependencies: List[str] = None
    ) -> bool:
        """Store query result in cache"""
        try:
            query_hash = self._hash_query(query)
            cache_key = self._generate_query_key(database, query_hash, params)

            cache_data = {
                "database": database,
                "query": query,
                "params": params,
                "result": result,
                "cached_at": time.time(),
                "ttl": ttl or self.default_ttl,
                "table_dependencies": table_dependencies or []
            }

            await self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl,
                json.dumps(cache_data, default=str)
            )

            # Also store in table dependency sets for invalidation
            if table_dependencies:
                for table in table_dependencies:
                    await self.redis_client.sadd(f"{self.cache_prefix}:table:{table}", cache_key)

            self.stats["sets"] += 1
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Query cache write error: {e}")
            return False

    async def invalidate_table_cache(self, database: str, table: str) -> int:
        """Invalidate all cached queries for a specific table"""
        try:
            # Get all cache keys for this table
            table_key = f"{self.cache_prefix}:table:{table}"
            cache_keys = await self.redis_client.smembers(table_key)

            if cache_keys:
                # Delete all cached queries for this table
                await self.redis_client.delete(*cache_keys)
                # Clean up the table set
                await self.redis_client.delete(table_key)

            self.stats["invalidations"] += len(cache_keys)
            return len(cache_keys)
        except Exception as e:
            print(f"Table cache invalidation error: {e}")
            return 0

    async def invalidate_database_cache(self, database: str) -> int:
        """Invalidate all cached queries for a database"""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            invalidated = 0
            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    if cache_info.get("database") == database:
                        await self.redis_client.delete(key)
                        invalidated += 1

            return invalidated
        except Exception as e:
            print(f"Database cache invalidation error: {e}")
            return 0

    async def invalidate_query_cache(self, database: str, query_pattern: str) -> int:
        """Invalidate cached queries matching a pattern"""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            invalidated = 0
            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    if (cache_info.get("database") == database and
                        query_pattern.lower() in cache_info.get("query", "").lower()):
                        await self.redis_client.delete(key)
                        invalidated += 1

            return invalidated
        except Exception as e:
            print(f"Query cache invalidation error: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get query cache statistics"""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            total_cached = len(keys)
            total_size = 0

            # Sample some entries to get stats
            sample_size = min(10, total_cached)
            if sample_size > 0:
                sample_keys = keys[:sample_size]
                for key in sample_keys:
                    size = await self.redis_client.strlen(key)
                    total_size += size

            avg_size = total_size // sample_size if sample_size > 0 else 0

            return {
                "total_cached_queries": total_cached,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "invalidations": self.stats["invalidations"],
                "errors": self.stats["errors"],
                "hit_rate_percent": round((self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) * 100), 2) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0,
                "estimated_size_bytes": total_size,
                "average_entry_size_bytes": avg_size,
                "default_ttl_seconds": self.default_ttl
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {"error": str(e)}


class CachedDatabaseManager:
    """Database manager with integrated query caching"""

    def __init__(self):
        self.query_cache = DatabaseQueryCache()
        # These would be actual database connections in production
        self.postgres_pool = None
        self.mongodb_client = None

    async def cached_postgres_query(
        self,
        query: str,
        params: Dict = None,
        ttl: int = None,
        table_dependencies: List[str] = None,
        invalidate_on_write: bool = True
    ):
        """Execute PostgreSQL query with caching"""
        # Check cache first
        cached_result = await self.query_cache.get_cached_query("postgresql", query, params)
        if cached_result is not None:
            return cached_result

        # Execute query (placeholder - would use actual DB connection)
        # In production, this would be:
        # result = await self.postgres_pool.fetch(query, *params) if params else await self.postgres_pool.fetch(query)

        # For demo purposes, return mock data based on query type
        if "SELECT" in query.upper():
            if "users" in query.lower():
                result = [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
                ]
            else:
                result = [{"id": 1, "name": "Mock Data", "cached": True}]
        else:
            result = {"affected_rows": 1}

        # Cache the result
        await self.query_cache.set_cached_query("postgresql", query, params, result, ttl, table_dependencies)

        return result

    async def cached_mongodb_query(
        self,
        collection: str,
        query: Dict,
        ttl: int = None,
        invalidate_on_write: bool = True
    ):
        """Execute MongoDB query with caching"""
        query_str = json.dumps(query, sort_keys=True)
        cache_key = f"mongodb:{collection}:{hashlib.md5(query_str.encode()).hexdigest()}"

        # Check cache first
        cached_result = await self.query_cache.get_cached_query("mongodb", query_str, {"collection": collection})
        if cached_result is not None:
            return cached_result

        # Execute query (placeholder - would use actual DB connection)
        # result = await self.mongodb_client[collection].find_one(query)

        # For demo purposes, return mock data
        result = {
            "_id": "507f1f77bcf86cd799439011",
            "collection": collection,
            "data": query,
            "cached": True
        }

        # Cache the result
        await self.query_cache.set_cached_query("mongodb", query_str, {"collection": collection}, result, ttl)

        return result

    async def invalidate_table_data(self, database: str, table: str) -> int:
        """Invalidate cached data for specific table"""
        return await self.query_cache.invalidate_table_cache(database, table)

    async def get_cache_performance(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        return await self.query_cache.get_cache_stats()


# Global database cache manager
db_cache_manager = CachedDatabaseManager()
