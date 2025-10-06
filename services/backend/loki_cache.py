"""
Loki + Promtail Cache Integration for FastAPI
Log query caching and optimization
"""
import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional

from .client import get_redis_client


class LokiCacheManager:
    """Advanced Loki log query caching with Redis"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_prefix = "loki_cache"

        # Cache statistics
        self.stats = {
            "query_hits": 0,
            "query_misses": 0,
            "log_hits": 0,
            "log_misses": 0,
            "cache_invalidations": 0,
            "errors": 0
        }

    def _generate_query_key(self, query: str, start_time: float, end_time: float, limit: int = 1000) -> str:
        """Generate cache key for log query"""
        key_data = {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "limit": limit
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:query:{cache_key}"

    def _generate_log_key(self, log_hash: str, timestamp: float) -> str:
        """Generate cache key for log data"""
        key_data = {
            "log_hash": log_hash,
            "timestamp": timestamp
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:log:{cache_key}"

    async def cache_query_result(
        self,
        query: str,
        result: List[Dict[str, Any]],
        start_time: float,
        end_time: float,
        limit: int = 1000,
        ttl: int = 300
    ) -> bool:
        """Cache Loki query result"""
        try:
            cache_key = self._generate_query_key(query, start_time, end_time, limit)

            cache_data = {
                "query": query,
                "result": result,
                "start_time": start_time,
                "end_time": end_time,
                "limit": limit,
                "cached_at": time.time(),
                "ttl": ttl,
                "result_count": len(result)
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Loki query cache error: {e}")
            return False

    async def get_cached_query_result(
        self,
        query: str,
        start_time: float,
        end_time: float,
        limit: int = 1000
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached Loki query result"""
        try:
            cache_key = self._generate_query_key(query, start_time, end_time, limit)
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
            print(f"Loki query retrieval error: {e}")
            return None

    async def cache_log_data(
        self,
        log_hash: str,
        log_data: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:
        """Cache individual log entry"""
        try:
            cache_key = self._generate_log_key(log_hash, log_data.get("timestamp", time.time()))

            cache_data = {
                "log_hash": log_hash,
                "data": log_data,
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
            print(f"Loki log cache error: {e}")
            return False

    async def get_cached_log_data(self, log_hash: str, timestamp: float) -> Optional[Dict[str, Any]]:
        """Get cached log data"""
        try:
            cache_key = self._generate_log_key(log_hash, timestamp)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                cache_info = json.loads(cached_data)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < cache_info.get("ttl", 3600):
                    self.stats["log_hits"] += 1
                    return cache_info["data"]

            self.stats["log_misses"] += 1
            return None

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Loki log retrieval error: {e}")
            return None

    async def analyze_log_patterns(self) -> Dict[str, Any]:
        """Analyze log patterns for optimization"""
        try:
            pattern = f"{self.cache_prefix}:log:*"
            keys = await self.redis_client.keys(pattern)

            pattern_analysis = {}

            for key in keys[:100]:  # Analyze first 100 logs
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    log_info = json.loads(cached_data)
                    log_data = log_info.get("data", {})

                    # Extract patterns (simplified)
                    level = log_data.get("level", "info")
                    source = log_data.get("source", "unknown")

                    pattern_key = f"{level}:{source}"

                    if pattern_key not in pattern_analysis:
                        pattern_analysis[pattern_key] = {
                            "count": 0,
                            "sample_logs": []
                        }

                    pattern_analysis[pattern_key]["count"] += 1

                    if len(pattern_analysis[pattern_key]["sample_logs"]) < 3:
                        pattern_analysis[pattern_key]["sample_logs"].append(log_data.get("message", ""))

            # Identify hot patterns
            hot_patterns = sorted(
                [{"pattern": pattern, "count": data["count"]} for pattern, data in pattern_analysis.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:10]

            return {
                "total_logs_analyzed": len(keys),
                "patterns_found": len(pattern_analysis),
                "hot_patterns": hot_patterns,
                "recommendations": [
                    "Preload frequently accessed log patterns",
                    "Implement log level-based caching strategies",
                    "Consider log compression for high-volume patterns"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    async def preload_common_queries(self, common_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preload commonly used log queries"""
        try:
            preload_results = {}

            for query_info in common_queries:
                query = query_info.get("query")
                time_range = query_info.get("time_range", {"start": "-1h", "end": "now"})

                # Simulate Loki query result
                mock_result = [
                    {
                        "timestamp": time.time() * 1000000000,
                        "level": "info",
                        "message": f"Preloaded log for query: {query}",
                        "source": "preload"
                    }
                ]

                success = await self.cache_query_result(
                    query,
                    mock_result,
                    time.time() - 3600,
                    time.time(),
                    100,
                    600
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

        total_log_requests = self.stats["log_hits"] + self.stats["log_misses"]
        log_hit_rate = (self.stats["log_hits"] / total_log_requests * 100) if total_log_requests > 0 else 0

        try:
            # Get cache size information
            query_pattern = f"{self.cache_prefix}:query:*"
            log_pattern = f"{self.cache_prefix}:log:*"

            query_keys = await self.redis_client.keys(query_pattern)
            log_keys = await self.redis_client.keys(log_pattern)

            query_size = sum(await self.redis_client.strlen(key) for key in query_keys[:50])
            log_size = sum(await self.redis_client.strlen(key) for key in log_keys[:50])

            return {
                "query_cache": {
                    "hits": self.stats["query_hits"],
                    "misses": self.stats["query_misses"],
                    "hit_rate_percent": round(query_hit_rate, 2),
                    "cached_queries": len(query_keys)
                },
                "log_cache": {
                    "hits": self.stats["log_hits"],
                    "misses": self.stats["log_misses"],
                    "hit_rate_percent": round(log_hit_rate, 2),
                    "cached_logs": len(log_keys)
                },
                "cache_size_bytes": {
                    "queries": query_size,
                    "logs": log_size,
                    "total": query_size + log_size
                },
                "invalidations": self.stats["cache_invalidations"],
                "errors": self.stats["errors"],
                "overall_hit_rate": round((query_hit_rate + log_hit_rate) / 2, 2),
                "performance_improvement": f"{round((query_hit_rate + log_hit_rate) / 2, 1)}%"
            }
        except Exception as e:
            return {"error": str(e)}


# Global Loki cache manager
loki_cache_manager = LokiCacheManager()
