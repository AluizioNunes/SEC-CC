"""
SEC Backend Package
Organized backend services for the SEC application.
"""

# AI Services
from .AI import UltraAIService, AIProvider, AIModel, PredictionRequest, PredictionResult, ultra_ai_service
from .AI.nlp import AdvancedNLPService, NLPAnalysisType, NLPAnalysisRequest, advanced_nlp_service
from .AI.multimedia import MultimediaContentGenerationService, MediaType, ContentGenerationType, ContentGenerationRequest, multimedia_content_service
from .AI.analysis import SentimentBehaviorAnalysisService, AnalysisType, SentimentType, BehaviorPattern, AnalysisRequest, sentiment_behavior_service

# Security Services
from .Security import UltraSecurityService, SecurityClassification, ThreatLevel, ultra_security_service
from .Security.oauth2 import OAuth2ProviderService, OAuth2Provider, OAuth2Client, OAuth2Token, oauth2_provider
from .Security.biometric import BiometricAuthService, BiometricType, BiometricSecurityLevel, BiometricTemplate, BiometricAuthenticationResult, biometric_auth
from .Security.encryption import DataEncryptionService, EncryptionAlgorithm, KeyType, EncryptionKey, EncryptedData, data_encryption

# Analytics Services
from .Analytics import UltraAnalyticsService, AnalyticsScope, ultra_analytics_service
from .Analytics import BusinessIntelligenceService, business_intelligence_service
from .Analytics.bi import BusinessIntelligenceDashboardService, DashboardType, VisualizationType, bi_dashboard_service

# Redis Client
from .Redis import get_redis_client, close_redis_connection, test_redis_connection

# Service Mesh
from .Service_Mesh import ServiceMesh, ServiceStatus, service_mesh

# Message Broker
from .Message_Broker import HybridMessageBroker, MessageBrokerType, MessagePriority, hybrid_broker, message_handler

# API Gateway
from .API_Gateway import APIGateway, api_gateway

# Service Registry
from .Service_Registry import ServiceRegistry, service_registry

# Event-Driven Architecture
from .Event_Driven import EventDrivenSystem, EventType, SagaStatus, event_driven_system

# Service Registration
from .Service_Registration import ServiceRegistration, service_registration, register_current_service, unregister_current_service

__all__ = [
    # AI Services
    "UltraAIService", "AIProvider", "AIModel", "PredictionRequest", "PredictionResult", "ultra_ai_service",
    "AdvancedNLPService", "NLPAnalysisType", "NLPAnalysisRequest", "advanced_nlp_service",
    "MultimediaContentGenerationService", "MediaType", "ContentGenerationType", "ContentGenerationRequest", "multimedia_content_service",
    "SentimentBehaviorAnalysisService", "AnalysisType", "SentimentType", "BehaviorPattern", "AnalysisRequest", "sentiment_behavior_service",
    
    # Security Services
    "UltraSecurityService", "SecurityClassification", "ThreatLevel", "ultra_security_service",
    "OAuth2ProviderService", "OAuth2Provider", "OAuth2Client", "OAuth2Token", "oauth2_provider",
    "BiometricAuthService", "BiometricType", "BiometricSecurityLevel", "BiometricTemplate", "BiometricAuthenticationResult", "biometric_auth",
    "DataEncryptionService", "EncryptionAlgorithm", "KeyType", "EncryptionKey", "EncryptedData", "data_encryption",
    
    # Analytics Services
    "UltraAnalyticsService", "AnalyticsScope", "ultra_analytics_service",
    "BusinessIntelligenceService", "business_intelligence_service",
    "BusinessIntelligenceDashboardService", "DashboardType", "VisualizationType", "bi_dashboard_service",
    
    # Redis Client
    "get_redis_client", "close_redis_connection", "test_redis_connection",
    
    # Service Mesh
    "ServiceMesh", "ServiceStatus", "service_mesh",
    
    # Message Broker
    "HybridMessageBroker", "MessageBrokerType", "MessagePriority", "hybrid_broker", "message_handler",
    
    # API Gateway
    "APIGateway", "api_gateway",
    
    # Service Registry
    "ServiceRegistry", "service_registry",
    
    # Event-Driven Architecture
    "EventDrivenSystem", "EventType", "SagaStatus", "event_driven_system",
    
    # Service Registration
    "ServiceRegistration", "service_registration", "register_current_service", "unregister_current_service",
]