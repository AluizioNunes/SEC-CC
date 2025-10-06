"""
Prometheus + Redis Integration - Metrics Caching
Advanced metrics caching and query optimization
"""
import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from .client import get_redis_client


class PrometheusCacheManager:
    """Advanced Prometheus metrics caching with Redis"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_prefix = "prometheus_cache"

        # Cache statistics
        self.stats = {
            "query_hits": 0,
            "query_misses": 0,
            "metric_hits": 0,
            "metric_misses": 0,
            "cache_invalidations": 0,
            "errors": 0
        }

    def _generate_query_key(self, query: str, start_time: float, end_time: float, step: float = 60.0) -> str:
        """Generate cache key for Prometheus query"""
        key_data = {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "step": step
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:query:{cache_key}"

    def _generate_metric_key(self, metric_name: str, labels: Dict[str, str] = None) -> str:
        """Generate cache key for metric data"""
        key_data = {
            "metric_name": metric_name,
            "labels": labels or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:metric:{cache_key}"

    async def cache_query_result(
        self,
        query: str,
        result: Dict[str, Any],
        start_time: float,
        end_time: float,
        step: float = 60.0,
        ttl: int = 300
    ) -> bool:
        """Cache Prometheus query result"""
        try:
            cache_key = self._generate_query_key(query, start_time, end_time, step)

            cache_data = {
                "query": query,
                "result": result,
                "start_time": start_time,
                "end_time": end_time,
                "step": step,
                "cached_at": time.time(),
                "ttl": ttl,
                "data_points": self._count_data_points(result)
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Prometheus query cache error: {e}")
            return False

    async def get_cached_query_result(
        self,
        query: str,
        start_time: float,
        end_time: float,
        step: float = 60.0
    ) -> Optional[Dict[str, Any]]:
        """Get cached Prometheus query result"""
        try:
            cache_key = self._generate_query_key(query, start_time, end_time, step)
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
            print(f"Prometheus query retrieval error: {e}")
            return None

    async def cache_metric_data(
        self,
        metric_name: str,
        data: List[Dict[str, Any]],
        labels: Dict[str, str] = None,
        ttl: int = 300
    ) -> bool:
        """Cache individual metric data"""
        try:
            cache_key = self._generate_metric_key(metric_name, labels)

            cache_data = {
                "metric_name": metric_name,
                "data": data,
                "labels": labels or {},
                "cached_at": time.time(),
                "ttl": ttl,
                "data_points": len(data)
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Prometheus metric cache error: {e}")
            return False

    async def get_cached_metric_data(
        self,
        metric_name: str,
        labels: Dict[str, str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached metric data"""
        try:
            cache_key = self._generate_metric_key(metric_name, labels)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                cache_info = json.loads(cached_data)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < cache_info.get("ttl", 300):
                    self.stats["metric_hits"] += 1
                    return cache_info["data"]

            self.stats["metric_misses"] += 1
            return None

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Prometheus metric retrieval error: {e}")
            return None

    def _count_data_points(self, result: Dict[str, Any]) -> int:
        """Count data points in Prometheus result"""
        try:
            data_points = 0
            result_type = result.get("resultType", "")

            if result_type == "matrix":
                for series in result.get("result", []):
                    data_points += len(series.get("values", []))
            elif result_type == "vector":
                data_points = len(result.get("result", []))
            elif result_type == "scalar":
                data_points = 1

            return data_points
        except Exception:
            return 0

    async def invalidate_query_cache(self, query_pattern: str = None) -> int:
        """Invalidate query cache by pattern or all queries"""
        try:
            if query_pattern:
                pattern = f"{self.cache_prefix}:query:*{query_pattern}*"
            else:
                pattern = f"{self.cache_prefix}:query:*"

            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)

            return len(keys)
        except Exception as e:
            print(f"Query invalidation error: {e}")
            return 0

    async def invalidate_metric_cache(self, metric_name: str = None) -> int:
        """Invalidate metric cache by name or all metrics"""
        try:
            if metric_name:
                pattern = f"{self.cache_prefix}:metric:*{metric_name}*"
            else:
                pattern = f"{self.cache_prefix}:metric:*"

            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)

            return len(keys)
        except Exception as e:
            print(f"Metric invalidation error: {e}")
            return 0

    async def get_query_performance_analysis(self) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        try:
            pattern = f"{self.cache_prefix}:query:*"
            keys = await self.redis_client.keys(pattern)

            query_analysis = {}

            for key in keys[:50]:  # Analyze first 50 queries
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    query = cache_info.get("query", "")

                    if query not in query_analysis:
                        query_analysis[query] = {
                            "execution_count": 0,
                            "total_data_points": 0,
                            "cache_ttl": cache_info.get("ttl", 300)
                        }

                    query_analysis[query]["execution_count"] += 1
                    query_analysis[query]["total_data_points"] += cache_info.get("data_points", 0)

            # Identify optimization opportunities
            optimizations = []

            for query, stats in query_analysis.items():
                if stats["total_data_points"] > 10000:  # High data volume queries
                    optimizations.append({
                        "query": query[:50] + "..." if len(query) > 50 else query,
                        "issue": "High data volume",
                        "suggestion": "Consider reducing time range or increasing aggregation",
                        "data_points": stats["total_data_points"]
                    })

                if stats["execution_count"] > 10:  # Frequently executed queries
                    optimizations.append({
                        "query": query[:50] + "..." if len(query) > 50 else query,
                        "issue": "Frequently executed",
                        "suggestion": "Consider increasing cache TTL",
                        "execution_count": stats["execution_count"]
                    })

            return {
                "total_queries_analyzed": len(query_analysis),
                "optimizations": optimizations,
                "query_frequency": query_analysis,
                "recommendations": [
                    "Increase TTL for frequently accessed queries",
                    "Reduce time ranges for high-volume queries",
                    "Implement query result aggregation",
                    "Consider step size optimization"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_hot_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed metrics"""
        try:
            pattern = f"{self.cache_prefix}:metric:*"
            keys = await self.redis_client.keys(pattern)

            metric_access = {}

            for key in keys:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    cache_info = json.loads(cached_data)
                    metric_name = cache_info.get("metric_name")

                    if metric_name not in metric_access:
                        metric_access[metric_name] = 0

                    metric_access[metric_name] += 1

            # Sort by access count
            sorted_metrics = sorted(
                [{"metric": metric, "access_count": count} for metric, count in metric_access.items()],
                key=lambda x: x["access_count"],
                reverse=True
            )

            return sorted_metrics[:limit]

        except Exception as e:
            return []

    async def preload_common_queries(self, common_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preload commonly used Prometheus queries"""
        try:
            preload_results = {}

            for query_info in common_queries:
                query = query_info.get("query")
                time_range = query_info.get("time_range", {"start": "-1h", "end": "now"})

                # Simulate query execution (in real implementation, this would call Prometheus API)
                mock_result = {
                    "status": "success",
                    "data": {
                        "resultType": "matrix",
                        "result": [
                            {
                                "metric": {"__name__": "up", "job": "prometheus"},
                                "values": [[time.time(), "1"], [time.time() - 60, "1"]]
                            }
                        ]
                    }
                }

                success = await self.cache_query_result(
                    query,
                    mock_result,
                    time.time() - 3600,  # 1 hour ago
                    time.time(),
                    step=60,
                    ttl=600  # 10 minutes
                )

                preload_results[query] = success

            successful_preloads = sum(1 for success in preload_results.values() if success)

            return {
                "preloaded_queries": len(common_queries),
                "successful_preloads": successful_preloads,
                "preload_results": preload_results
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_query_requests = self.stats["query_hits"] + self.stats["query_misses"]
        query_hit_rate = (self.stats["query_hits"] / total_query_requests * 100) if total_query_requests > 0 else 0

        total_metric_requests = self.stats["metric_hits"] + self.stats["metric_misses"]
        metric_hit_rate = (self.stats["metric_hits"] / total_metric_requests * 100) if total_metric_requests > 0 else 0

        try:
            # Get cache size information
            query_pattern = f"{self.cache_prefix}:query:*"
            metric_pattern = f"{self.cache_prefix}:metric:*"

            query_keys = await self.redis_client.keys(query_pattern)
            metric_keys = await self.redis_client.keys(metric_pattern)

            query_size = sum(await self.redis_client.strlen(key) for key in query_keys[:50])
            metric_size = sum(await self.redis_client.strlen(key) for key in metric_keys[:50])

            return {
                "query_cache": {
                    "hits": self.stats["query_hits"],
                    "misses": self.stats["query_misses"],
                    "hit_rate_percent": round(query_hit_rate, 2),
                    "cached_queries": len(query_keys)
                },
                "metric_cache": {
                    "hits": self.stats["metric_hits"],
                    "misses": self.stats["metric_misses"],
                    "hit_rate_percent": round(metric_hit_rate, 2),
                    "cached_metrics": len(metric_keys)
                },
                "cache_size_bytes": {
                    "queries": query_size,
                    "metrics": metric_size,
                    "total": query_size + metric_size
                },
                "invalidations": self.stats["cache_invalidations"],
                "errors": self.stats["errors"],
                "overall_hit_rate": round((query_hit_rate + metric_hit_rate) / 2, 2),
                "performance_improvement": f"{round((query_hit_rate + metric_hit_rate) / 2, 1)}%"
            }
        except Exception as e:
            return {"error": str(e)}


# Global Prometheus cache manager
prometheus_cache_manager = PrometheusCacheManager()
