"""
Redis Advanced Features Package - Production Ready
Complete Redis integration with modular structure
"""

# Core Redis client
from .client import get_redis_client, close_redis_connection, test_redis_connection

# API Response Caching
from .api_cache import (
    APICacheManager, cache_response, api_cache_manager,
    get_cache_stats, invalidate_cache_by_tags, invalidate_cache_by_pattern
)

# Session Clustering (Multi-instance)
from .session_cluster import SessionCluster, session_cluster

# Distributed Rate Limiting
from .rate_limiter import DistributedRateLimiter, rate_limiter, RateLimitAlgorithm

# Database Query Caching
from .database_query_cache import DatabaseQueryCache, CachedDatabaseManager, db_cache_manager

# Advanced Data Structures
from .data_structures import RedisDataStructures, redis_ds

# Controllers and Middleware
from .advanced_controller import router as redis_router
from .middleware import (
    global_rate_limiting_middleware,
    session_middleware,
    request_logging_middleware
)

__all__ = [
    # Core
    "get_redis_client", "close_redis_connection", "test_redis_connection",

    # API Cache
    "APICacheManager", "cache_response", "api_cache_manager",
    "get_cache_stats", "invalidate_cache_by_tags", "invalidate_cache_by_pattern",

    # Session Clustering
    "SessionCluster", "session_cluster",

    # Rate Limiting
    "DistributedRateLimiter", "rate_limiter", "RateLimitAlgorithm",

    # Database Cache
    "DatabaseQueryCache", "CachedDatabaseManager", "db_cache_manager",

    # Data Structures
    "RedisDataStructures", "redis_ds",

    # Controllers and middleware
    "redis_router",
    "global_rate_limiting_middleware",
    "session_middleware",
    "request_logging_middleware"
]
