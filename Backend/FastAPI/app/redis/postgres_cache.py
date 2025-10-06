"""
PostgreSQL + Redis Integration - Advanced Query Caching
Real database integration with intelligent query caching and optimization
"""
import asyncio
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple, Union
from contextlib import asynccontextmanager

import asyncpg
from .client import get_redis_client


class PostgreSQLCacheManager:
    """Advanced PostgreSQL query caching with Redis"""

    def __init__(self, connection_string: str = None):
        self.redis_client = get_redis_client()
        self.connection_string = connection_string or "postgresql://user:password@localhost:5432/sec_cc"
        self.pool: Optional[asyncpg.Pool] = None
        self.cache_prefix = "postgres_cache"

        # Performance statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "queries_executed": 0,
            "cache_invalidations": 0,
            "errors": 0
        }

    async def initialize(self, min_size: int = 5, max_size: int = 20):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60,
                server_settings={
                    'jit': 'off',  # Disable JIT for predictable performance
                    'application_name': 'FastAPI-PostgreSQL-Cache'
                }
            )
            print("✅ PostgreSQL connection pool initialized")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            raise

    async def close(self):
        """Close PostgreSQL connection pool"""
        if self.pool:
            await self.pool.close()

    def _generate_query_key(self, query: str, params: Tuple = None) -> str:
        """Generate unique cache key for query"""
        key_data = {
            "query": query,
            "params": params or ()
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_key}"

    async def _get_table_dependencies(self, query: str) -> List[str]:
        """Extract table names from query for dependency tracking"""
        import re

        # Simple regex to find table names (can be enhanced)
        table_pattern = r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)|\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, query, re.IGNORECASE)

        tables = []
        for match in matches:
            for table in match:
                if table:
                    tables.append(table.lower())

        return list(set(tables))

    async def cached_query(
        self,
        query: str,
        params: Tuple = None,
        ttl: int = 300,
        table_dependencies: List[str] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute PostgreSQL query with intelligent caching
        """
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_query_key(query, params)

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = await self.redis_client.get(cache_key)
            if cached_result:
                cache_info = json.loads(cached_result)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < ttl:
                    self.stats["cache_hits"] += 1
                    return cache_info["result"]

        self.stats["cache_misses"] += 1

        # Execute query
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *params) if params else await connection.fetch(query)

                # Convert to list of dicts
                rows = [dict(record) for record in result]

                # Auto-detect table dependencies if not provided
                if table_dependencies is None:
                    table_dependencies = await self._get_table_dependencies(query)

                # Cache the result
                cache_data = {
                    "result": rows,
                    "cached_at": time.time(),
                    "ttl": ttl,
                    "table_dependencies": table_dependencies,
                    "query": query,
                    "execution_time": time.time() - start_time
                }

                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cache_data, default=str)
                )

                # Store in table dependency sets for invalidation
                for table in table_dependencies:
                    await self.redis_client.sadd(f"{self.cache_prefix}:table:{table}", cache_key)

                self.stats["queries_executed"] += 1
                return rows

        except Exception as e:
            self.stats["errors"] += 1
            print(f"PostgreSQL query error: {e}")
            raise

    async def cached_query_val(self, query: str, params: Tuple = None) -> Any:
        """Execute query expecting single value"""
        result = await self.cached_query(query, params, ttl=300)
        return result[0] if result else None

    async def cached_query_row(self, query: str, params: Tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query expecting single row"""
        result = await self.cached_query(query, params, ttl=300)
        return result[0] if result else None

    async def invalidate_table_cache(self, table: str) -> int:
        """Invalidate all cached queries for a specific table"""
        try:
            table_key = f"{self.cache_prefix}:table:{table.lower()}"
            cache_keys = await self.redis_client.smembers(table_key)

            if cache_keys:
                # Delete all cached queries for this table
                await self.redis_client.delete(*cache_keys)
                # Clean up the table set
                await self.redis_client.delete(table_key)

            self.stats["cache_invalidations"] += len(cache_keys)
            return len(cache_keys)
        except Exception as e:
            print(f"Table invalidation error: {e}")
            return 0

    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cached queries for a specific user"""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            invalidated = 0
            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    result = cache_info.get("result", [])

                    # Check if any row contains the user_id
                    for row in result:
                        if isinstance(row, dict) and str(row.get("id", row.get("user_id", ""))) == str(user_id):
                            await self.redis_client.delete(key)
                            invalidated += 1
                            break

            return invalidated
        except Exception as e:
            print(f"User cache invalidation error: {e}")
            return 0

    async def execute_write_query(self, query: str, params: Tuple = None) -> str:
        """Execute write query and invalidate related caches"""
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(query, *params) if params else await connection.execute(query)

                # Extract table names from write query for cache invalidation
                table_dependencies = await self._get_table_dependencies(query)

                # Invalidate caches for affected tables
                for table in table_dependencies:
                    await self.invalidate_table_cache(table)

                return result
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Write query error: {e}")
            raise

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache performance statistics"""
        total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_rate = (self.stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0

        # Get cache size information
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)
            total_size = sum(await self.redis_client.strlen(key) for key in keys[:100])  # Sample

            return {
                "cache_hits": self.stats["cache_hits"],
                "cache_misses": self.stats["cache_misses"],
                "queries_executed": self.stats["queries_executed"],
                "cache_invalidations": self.stats["cache_invalidations"],
                "errors": self.stats["errors"],
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "estimated_cache_size_bytes": total_size,
                "cached_queries": len(keys),
                "performance_improvement": f"{round(hit_rate, 1)}%"
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_table_cache_info(self, table: str) -> Dict[str, Any]:
        """Get cache information for specific table"""
        try:
            table_key = f"{self.cache_prefix}:table:{table.lower()}"
            cache_keys = await self.redis_client.smembers(table_key)

            return {
                "table": table,
                "cached_queries": len(cache_keys),
                "cache_keys": list(cache_keys)[:10]  # First 10 for preview
            }
        except Exception as e:
            return {"error": str(e)}

    async def optimize_query_performance(self) -> Dict[str, Any]:
        """Analyze and suggest query optimizations"""
        try:
            # Get slow queries (placeholder - would need pg_stat_statements)
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            optimizations = []

            for key in keys[:50]:  # Analyze first 50 queries
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    execution_time = cache_info.get("execution_time", 0)

                    if execution_time > 0.1:  # Queries slower than 100ms
                        optimizations.append({
                            "query_hash": key.split(":")[-1],
                            "execution_time": execution_time,
                            "suggestion": "Consider adding database indexes or query optimization"
                        })

            return {
                "slow_queries_found": len(optimizations),
                "optimizations": optimizations,
                "recommendation": "Review and optimize slow queries"
            }
        except Exception as e:
            return {"error": str(e)}


# Global PostgreSQL cache manager instance
postgres_cache_manager = PostgreSQLCacheManager()
