"""
Redis Advanced Features Package - Production Ready
Complete Redis integration with all advanced features
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

# PostgreSQL Integration
from .postgres_cache import PostgreSQLCacheManager, postgres_cache_manager

# MongoDB Integration
from .mongodb_cache import MongoDBCacheManager, mongodb_cache_manager

# RabbitMQ + Redis Hybrid
from .hybrid_broker import HybridMessageBroker, hybrid_broker, MessageBrokerType, MessagePriority

# Redis Streams - Event Sourcing
from .event_sourcing import EventSourcingManager, event_sourcing_manager, Event, EventType

# Grafana Dashboard Caching
from .grafana_cache import GrafanaCacheManager, grafana_cache_manager

# Prometheus Metrics Caching
from .prometheus_cache import PrometheusCacheManager, prometheus_cache_manager

# Loki Log Caching
from .loki_cache import LokiCacheManager, loki_cache_manager

# Advanced Data Structures
from .data_structures import RedisDataStructures, redis_ds

# Controllers and Middleware
from .advanced_controller import router as redis_router
from .advanced_demo_controller import router as advanced_demo_router
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

    # PostgreSQL Integration
    "PostgreSQLCacheManager", "postgres_cache_manager",

    # MongoDB Integration
    "MongoDBCacheManager", "mongodb_cache_manager",

    # Message Broker
    "HybridMessageBroker", "hybrid_broker", "MessageBrokerType", "MessagePriority",

    # Event Sourcing
    "EventSourcingManager", "event_sourcing_manager", "Event", "EventType",

    # Monitoring Stack
    "GrafanaCacheManager", "grafana_cache_manager",
    "PrometheusCacheManager", "prometheus_cache_manager",
    "LokiCacheManager", "loki_cache_manager",

    # Data Structures
    "RedisDataStructures", "redis_ds",

    # Controllers and middleware
    "redis_router", "advanced_demo_router",
    "global_rate_limiting_middleware",
    "session_middleware",
    "request_logging_middleware"
]
