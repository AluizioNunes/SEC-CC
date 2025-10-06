"""
Redis Advanced Features Package - Ultra-Advanced Implementation
Complete Redis integration with all advanced features for revolutionary applications
"""

# Core Redis client
from .client import get_redis_client, close_redis_connection, test_redis_connection

# Basic caching and operations
from .cache import get_cache, set_cache, delete_cache, exists_cache
from .api_cache import (
    APICacheManager, cache_response, api_cache_manager,
    get_cache_stats, invalidate_cache_by_tags, invalidate_cache_by_pattern
)

# Session management
from .session_cluster import SessionCluster, session_cluster

# Rate limiting
from .rate_limiter import DistributedRateLimiter, rate_limiter, RateLimitAlgorithm

# Database integrations
from .database_query_cache import DatabaseQueryCache, CachedDatabaseManager, db_cache_manager
from .postgres_cache import PostgreSQLCacheManager, postgres_cache_manager
from .mongodb_cache import MongoDBCacheManager, mongodb_cache_manager

# Message broker
from .hybrid_broker import HybridMessageBroker, hybrid_broker, MessageBrokerType, MessagePriority

# Event sourcing and CQRS
from .event_sourcing import EventSourcingManager, event_sourcing_manager, Event, EventType
from .cqrs_manager import CQRSManager, cqrs_manager, Command, CommandStatus

# Machine Learning & AI
from .machine_learning import RecommendationEngine, PredictiveAnalytics, recommendation_engine, predictive_analytics

# Ultra-advanced features
from .global_service_mesh import GlobalServiceMesh, RegionStatus, global_service_mesh
from .ultra_ai_manager import UltraAIManager, AIModelType, ultra_ai_manager
from .ultra_security import UltraSecurityManager, SecurityClassification, ThreatLevel, ultra_security_manager
from .ultra_analytics import UltraAnalyticsEngine, AnalyticsScope, ultra_analytics_engine

# Advanced Search
from .advanced_search import AdvancedSearchEngine, search_engine

# Service Mesh
from .service_mesh import ServiceMesh, ServiceStatus, service_mesh

# Monitoring integrations
from .grafana_cache import GrafanaCacheManager, grafana_cache_manager
from .prometheus_cache import PrometheusCacheManager, prometheus_cache_manager
from .loki_cache import LokiCacheManager, loki_cache_manager

# Message analytics
from .message_analytics import MessageAnalytics, message_analytics

# Advanced data structures
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

    # Basic operations
    "get_cache", "set_cache", "delete_cache", "exists_cache",

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

    # Event Sourcing & CQRS
    "EventSourcingManager", "event_sourcing_manager", "Event", "EventType",
    "CQRSManager", "cqrs_manager", "Command", "CommandStatus",

    # Machine Learning & AI
    "RecommendationEngine", "PredictiveAnalytics", "recommendation_engine", "predictive_analytics",

    # Ultra-Advanced Features
    "GlobalServiceMesh", "RegionStatus", "global_service_mesh",
    "UltraAIManager", "AIModelType", "ultra_ai_manager",
    "UltraSecurityManager", "SecurityClassification", "ThreatLevel", "ultra_security_manager",
    "UltraAnalyticsEngine", "AnalyticsScope", "ultra_analytics_engine",

    # Advanced Search
    "AdvancedSearchEngine", "search_engine",

    # Service Mesh
    "ServiceMesh", "ServiceStatus", "service_mesh",

    # Monitoring Stack
    "GrafanaCacheManager", "grafana_cache_manager",
    "PrometheusCacheManager", "prometheus_cache_manager",
    "LokiCacheManager", "loki_cache_manager",

    # Message Analytics
    "MessageAnalytics", "message_analytics",

    # Data Structures
    "RedisDataStructures", "redis_ds",

    # Controllers and middleware
    "redis_router", "advanced_demo_router",
    "global_rate_limiting_middleware",
    "session_middleware",
    "request_logging_middleware"
]
