"""
Redis Integration Package for FastAPI
Integrates with the new organized Backend services
"""

from fastapi import APIRouter

# Create real FastAPI routers with the correct prefix and tags
redis_router = APIRouter(prefix="/redis-advanced", tags=["redis-advanced"])
advanced_demo_router = APIRouter(prefix="/redis-advanced", tags=["redis-advanced"])

# Import actual implementations from the organized Backend structure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import actual Redis client and related services
try:
    from Backend.Redis.client import get_redis_client, test_redis_connection
except ImportError:
    # Fallback to local Redis client if Backend module is not available
    from .local_redis_client import get_redis_client, test_redis_connection

# Import service mesh and registry
try:
    from Backend.Service_Mesh.service_mesh import service_mesh
    from Backend.Service_Registry.service_registry import service_registry
    from Backend.Service_Registration.service_registration import service_registration
except ImportError:
    # Create mock objects if Backend modules are not available
    service_mesh = None
    service_registry = None
    service_registration = None

# Import message broker
try:
    from Backend.Message_Broker.message_broker import hybrid_broker
    from Backend.Message_Broker.message_handler import message_handler
    from Backend.Message_Broker.message_producer import message_producer
except ImportError:
    # Create mock objects if Backend modules are not available
    hybrid_broker = None
    message_handler = None
    message_producer = None

# Import security services
try:
    from Backend.Security.security_service import ultra_security_service
    from Backend.Security.oauth2.oauth2_provider import oauth2_provider
    from Backend.Security.biometric.biometric_auth import biometric_auth
    from Backend.Security.encryption.data_encryption import data_encryption
except ImportError:
    # Create mock objects if Backend modules are not available
    ultra_security_service = None
    oauth2_provider = None
    biometric_auth = None
    data_encryption = None

# Import AI services
try:
    from Backend.AI.nlp.advanced_nlp import advanced_nlp_service
    from Backend.AI.multimedia.content_generation import multimedia_content_service
    from Backend.AI.analysis.sentiment_behavior import sentiment_behavior_service
except ImportError:
    # Create mock objects if Backend modules are not available
    advanced_nlp_service = None
    multimedia_content_service = None
    sentiment_behavior_service = None

# Import analytics services
try:
    from Backend.Analytics.business_intelligence import business_intelligence_service
    from Backend.Analytics.analytics_service import ultra_analytics_service
    from Backend.Analytics.bi.dashboard_service import bi_dashboard_service
    from Backend.Analytics.ml.ml_predictions import ml_predictions
    from Backend.Analytics.realtime.realtime_reports import realtime_reporting
except ImportError:
    # Create mock objects if Backend modules are not available
    business_intelligence_service = None
    ultra_analytics_service = None
    bi_dashboard_service = None
    ml_predictions = None
    realtime_reporting = None

# Import event driven system
try:
    from Backend.Event_Driven.event_driven import event_driven_system
except ImportError:
    # Create mock objects if Backend modules are not available
    event_driven_system = None

# Import API gateway
try:
    from Backend.API_Gateway.api_gateway import api_gateway
except ImportError:
    # Create mock objects if Backend modules are not available
    api_gateway = None

# Import middleware and cache managers
try:
    # Try to import from actual Redis integration
    from app.redis.middleware import global_rate_limiting_middleware, session_middleware, request_logging_middleware
    from app.redis.cache_managers import (
        api_cache_manager, session_cluster, rate_limiter, db_cache_manager,
        postgres_cache_manager, mongodb_cache_manager, event_sourcing_manager,
        grafana_cache_manager, prometheus_cache_manager, loki_cache_manager,
        global_service_mesh, ultra_ai_manager, ultra_security_manager, ultra_analytics_engine
    )
    from app.redis.event_types import EventType
except ImportError:
    # Fallback to mock implementations
    from app.redis.mock_components import (
        global_rate_limiting_middleware, session_middleware, request_logging_middleware,
        api_cache_manager, session_cluster, rate_limiter, db_cache_manager,
        postgres_cache_manager, mongodb_cache_manager, event_sourcing_manager,
        grafana_cache_manager, prometheus_cache_manager, loki_cache_manager,
        global_service_mesh, ultra_ai_manager, ultra_security_manager, ultra_analytics_engine,
        EventType
    )

# Re-export all the necessary components
__all__ = [
    # Routers
    "redis_router",
    "advanced_demo_router",
    
    # Redis client functions
    "get_redis_client",
    "test_redis_connection",
    
    # Service mesh and registry
    "service_mesh",
    "service_registry",
    "service_registration",
    
    # Message broker
    "hybrid_broker",
    "message_handler",
    "message_producer",
    
    # Security services
    "ultra_security_service",
    "oauth2_provider",
    "biometric_auth",
    "data_encryption",
    
    # AI services
    "advanced_nlp_service",
    "multimedia_content_service",
    "sentiment_behavior_service",
    
    # Analytics services
    "business_intelligence_service",
    "ultra_analytics_service",
    "bi_dashboard_service",
    "ml_predictions",
    "realtime_reporting",
    
    # Event driven system
    "event_driven_system",
    
    # API gateway
    "api_gateway",
    
    # Middleware
    "global_rate_limiting_middleware",
    "session_middleware",
    "request_logging_middleware",
    
    # Cache managers
    "api_cache_manager",
    "session_cluster",
    "rate_limiter",
    "db_cache_manager",
    "postgres_cache_manager",
    "mongodb_cache_manager",
    "event_sourcing_manager",
    "grafana_cache_manager",
    "prometheus_cache_manager",
    "loki_cache_manager",
    "global_service_mesh",
    "ultra_ai_manager",
    "ultra_security_manager",
    "ultra_analytics_engine",
    
    # Event types
    "EventType"
]