"""
Grafana + Redis Integration - Dashboard Caching
Advanced dashboard caching and optimization
"""
import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from .client import get_redis_client


class GrafanaCacheManager:
    """Advanced Grafana dashboard caching with Redis"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_prefix = "grafana_cache"

        # Cache statistics
        self.stats = {
            "dashboard_hits": 0,
            "query_hits": 0,
            "dashboard_misses": 0,
            "query_misses": 0,
            "cache_invalidations": 0,
            "errors": 0
        }

    def _generate_dashboard_key(self, dashboard_id: str, time_range: Dict[str, Any], variables: Dict[str, Any] = None) -> str:
        """Generate cache key for dashboard"""
        key_data = {
            "dashboard_id": dashboard_id,
            "time_range": time_range,
            "variables": variables or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:dashboard:{cache_key}"

    def _generate_query_key(self, query_hash: str, time_range: Dict[str, Any], variables: Dict[str, Any] = None) -> str:
        """Generate cache key for query result"""
        key_data = {
            "query_hash": query_hash,
            "time_range": time_range,
            "variables": variables or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:query:{cache_key}"

    async def cache_dashboard(
        self,
        dashboard_id: str,
        dashboard_data: Dict[str, Any],
        time_range: Dict[str, Any],
        variables: Dict[str, Any] = None,
        ttl: int = 300
    ) -> bool:
        """Cache complete dashboard"""
        try:
            cache_key = self._generate_dashboard_key(dashboard_id, time_range, variables)

            cache_data = {
                "dashboard_id": dashboard_id,
                "data": dashboard_data,
                "time_range": time_range,
                "variables": variables or {},
                "cached_at": time.time(),
                "ttl": ttl
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Dashboard cache error: {e}")
            return False

    async def get_cached_dashboard(
        self,
        dashboard_id: str,
        time_range: Dict[str, Any],
        variables: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached dashboard"""
        try:
            cache_key = self._generate_dashboard_key(dashboard_id, time_range, variables)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                cache_info = json.loads(cached_data)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < cache_info.get("ttl", 300):
                    self.stats["dashboard_hits"] += 1
                    return cache_info["data"]

            self.stats["dashboard_misses"] += 1
            return None

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Dashboard retrieval error: {e}")
            return None

    async def cache_query_result(
        self,
        query_hash: str,
        result: List[Dict[str, Any]],
        time_range: Dict[str, Any],
        variables: Dict[str, Any] = None,
        ttl: int = 300
    ) -> bool:
        """Cache query result"""
        try:
            cache_key = self._generate_query_key(query_hash, time_range, variables)

            cache_data = {
                "query_hash": query_hash,
                "result": result,
                "time_range": time_range,
                "variables": variables or {},
                "cached_at": time.time(),
                "ttl": ttl,
                "data_points": len(result)
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Query cache error: {e}")
            return False

    async def get_cached_query_result(
        self,
        query_hash: str,
        time_range: Dict[str, Any],
        variables: Dict[str, Any] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached query result"""
        try:
            cache_key = self._generate_query_key(query_hash, time_range, variables)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                cache_info = json.loads(cached_data)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < cache_info.get("ttl", 300):
                    self.stats["query_hits"] += 1
                    return cache_info["result"]

            self.stats["query_misses"] += 1
            return None

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Query result retrieval error: {e}")
            return None

    async def invalidate_dashboard_cache(self, dashboard_id: str) -> int:
        """Invalidate all cached data for a dashboard"""
        try:
            pattern = f"{self.cache_prefix}:dashboard:*"
            keys = await self.redis_client.keys(pattern)

            invalidated = 0
            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    if cache_info.get("dashboard_id") == dashboard_id:
                        await self.redis_client.delete(key)
                        invalidated += 1

            return invalidated
        except Exception as e:
            print(f"Dashboard invalidation error: {e}")
            return 0

    async def invalidate_query_cache(self, query_hash: str = None) -> int:
        """Invalidate query cache by hash or all queries"""
        try:
            if query_hash:
                pattern = f"{self.cache_prefix}:query:*{query_hash}*"
            else:
                pattern = f"{self.cache_prefix}:query:*"

            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)

            return len(keys)
        except Exception as e:
            print(f"Query invalidation error: {e}")
            return 0

    async def get_dashboard_usage_stats(self) -> Dict[str, Any]:
        """Get dashboard usage statistics"""
        try:
            pattern = f"{self.cache_prefix}:dashboard:*"
            keys = await self.redis_client.keys(pattern)

            dashboard_stats = {}
            for key in keys[:50]:  # Analyze first 50 dashboards
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    dashboard_id = cache_info.get("dashboard_id")

                    if dashboard_id not in dashboard_stats:
                        dashboard_stats[dashboard_id] = {
                            "access_count": 0,
                            "last_accessed": 0,
                            "cache_size": 0
                        }

                    dashboard_stats[dashboard_id]["access_count"] += 1
                    dashboard_stats[dashboard_id]["last_accessed"] = max(
                        dashboard_stats[dashboard_id]["last_accessed"],
                        cache_info.get("cached_at", 0)
                    )
                    dashboard_stats[dashboard_id]["cache_size"] += await self.redis_client.strlen(key)

            return {
                "total_dashboards": len(dashboard_stats),
                "dashboard_stats": dashboard_stats,
                "most_accessed": max(dashboard_stats.items(), key=lambda x: x[1]["access_count"]) if dashboard_stats else None
            }
        except Exception as e:
            return {"error": str(e)}

    async def optimize_dashboard_performance(self, dashboard_id: str) -> Dict[str, Any]:
        """Analyze and suggest dashboard optimizations"""
        try:
            # Get dashboard cache info
            dashboard_key = f"{self.cache_prefix}:dashboard:{dashboard_id}"

            optimizations = []

            # Check if dashboard exists in cache
            cached_data = await self.redis_client.get(dashboard_key)
            if not cached_data:
                optimizations.append({
                    "type": "missing_cache",
                    "suggestion": "Dashboard not cached - consider implementing caching",
                    "priority": "high"
                })

            # Check cache hit rates
            total_requests = self.stats["dashboard_hits"] + self.stats["dashboard_misses"]
            hit_rate = (self.stats["dashboard_hits"] / total_requests * 100) if total_requests > 0 else 0

            if hit_rate < 50:
                optimizations.append({
                    "type": "low_hit_rate",
                    "suggestion": f"Low cache hit rate ({hit_rate:.1f}%) - consider increasing TTL or optimizing queries",
                    "priority": "medium"
                })

            return {
                "dashboard_id": dashboard_id,
                "optimizations": optimizations,
                "current_hit_rate": hit_rate,
                "recommendations": [
                    "Increase query TTL for frequently accessed dashboards",
                    "Implement query result caching for expensive queries",
                    "Consider dashboard pre-loading for critical dashboards",
                    "Implement variable-based cache invalidation"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    async def preload_dashboard(self, dashboard_id: str, time_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preload dashboard for multiple time ranges"""
        try:
            preload_results = {}

            for time_range in time_ranges:
                # Simulate dashboard loading (in real implementation, this would call Grafana API)
                dashboard_data = {
                    "dashboard_id": dashboard_id,
                    "time_range": time_range,
                    "panels": [
                        {"id": 1, "title": "CPU Usage", "data": "preloaded"},
                        {"id": 2, "title": "Memory Usage", "data": "preloaded"}
                    ],
                    "preloaded": True,
                    "preload_time": time.time()
                }

                success = await self.cache_dashboard(dashboard_id, dashboard_data, time_range, ttl=600)
                preload_results[str(time_range)] = success

            successful_preloads = sum(1 for success in preload_results.values() if success)

            return {
                "dashboard_id": dashboard_id,
                "preloaded_ranges": len(time_ranges),
                "successful_preloads": successful_preloads,
                "preload_results": preload_results
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_dashboard_requests = self.stats["dashboard_hits"] + self.stats["dashboard_misses"]
        dashboard_hit_rate = (self.stats["dashboard_hits"] / total_dashboard_requests * 100) if total_dashboard_requests > 0 else 0

        total_query_requests = self.stats["query_hits"] + self.stats["query_misses"]
        query_hit_rate = (self.stats["query_hits"] / total_query_requests * 100) if total_query_requests > 0 else 0

        try:
            # Get cache size information
            dashboard_pattern = f"{self.cache_prefix}:dashboard:*"
            query_pattern = f"{self.cache_prefix}:query:*"

            dashboard_keys = await self.redis_client.keys(dashboard_pattern)
            query_keys = await self.redis_client.keys(query_pattern)

            dashboard_size = sum(await self.redis_client.strlen(key) for key in dashboard_keys[:50])
            query_size = sum(await self.redis_client.strlen(key) for key in query_keys[:50])

            return {
                "dashboard_cache": {
                    "hits": self.stats["dashboard_hits"],
                    "misses": self.stats["dashboard_misses"],
                    "hit_rate_percent": round(dashboard_hit_rate, 2),
                    "cached_dashboards": len(dashboard_keys)
                },
                "query_cache": {
                    "hits": self.stats["query_hits"],
                    "misses": self.stats["query_misses"],
                    "hit_rate_percent": round(query_hit_rate, 2),
                    "cached_queries": len(query_keys)
                },
                "cache_size_bytes": {
                    "dashboards": dashboard_size,
                    "queries": query_size,
                    "total": dashboard_size + query_size
                },
                "invalidations": self.stats["cache_invalidations"],
                "errors": self.stats["errors"],
                "overall_hit_rate": round((dashboard_hit_rate + query_hit_rate) / 2, 2),
                "performance_improvement": f"{round((dashboard_hit_rate + query_hit_rate) / 2, 1)}%"
            }
        except Exception as e:
            return {"error": str(e)}


# Global Grafana cache manager
grafana_cache_manager = GrafanaCacheManager()
