"""
Event types for FastAPI Redis integration
Defines various event types used in the application
"""


class EventType:
    """Event types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATABASE_CONNECTION_LOST = "database_connection_lost"
    EXTERNAL_API_FAILURE = "external_api_failure"
    AI_MODEL_UPDATE = "ai_model_update"
    CACHE_INVALIDATION = "cache_invalidation"
    MESSAGE_QUEUE_BACKLOG = "message_queue_backlog"