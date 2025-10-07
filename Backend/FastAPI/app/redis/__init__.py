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
from Backend.Redis import get_redis_client, test_redis_connection

# Import service mesh and registry
from Backend.Service_Mesh import service_mesh
from Backend.Service_Registry import service_registry
from Backend.Service_Registration import service_registration

# Import message broker
from Backend.Message_Broker import hybrid_broker, message_handler, message_producer

# Import security services
from Backend.Security import ultra_security_service
from Backend.Security.oauth2 import oauth2_provider
from Backend.Security.biometric import biometric_auth
from Backend.Security.encryption import data_encryption

# Import AI services
from Backend.AI import advanced_nlp_service, multimedia_content_service, sentiment_behavior_service

# Import analytics services
from Backend.Analytics import business_intelligence_service, ultra_analytics_service
from Backend.Analytics.bi import bi_dashboard_service
from Backend.Analytics.ml import ml_predictions
from Backend.Analytics.realtime import realtime_reporting

# Import event driven system
from Backend.Event_Driven import event_driven_system

# Import API gateway
from Backend.API_Gateway import api_gateway

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
    "api_gateway"
]