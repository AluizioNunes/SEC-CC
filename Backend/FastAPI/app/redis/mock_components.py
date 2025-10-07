"""
Mock components for FastAPI Redis integration
Provides fallback implementations when Backend modules are not available
"""

from fastapi import Request, Response
from typing import Callable, Awaitable, Dict, Any
import time


# Mock middleware functions
async def global_rate_limiting_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Mock rate limiting middleware"""
    response = await call_next(request)
    return response


async def session_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Mock session middleware"""
    response = await call_next(request)
    return response


async def request_logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Mock request logging middleware"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Mock cache managers
class MockCacheManager:
    """Mock cache manager"""
    def get_cache_stats(self) -> Dict[str, Any]:
        return {"status": "mock", "hits": 0, "misses": 0}
    
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    async def get_cache_performance(self):
        return {"status": "mock", "performance": "normal"}


class MockSessionCluster:
    """Mock session cluster"""
    async def get_session_stats(self):
        return {"status": "mock", "active_sessions": 0}
    
    async def start_heartbeat(self):
        pass


class MockRateLimiter:
    """Mock rate limiter"""
    def get_rate_limit_stats(self):
        return {"status": "mock", "requests": 0}


class MockEventSourcingManager:
    """Mock event sourcing manager"""
    async def get_event_stats(self):
        return {"status": "mock", "events": 0}


class MockServiceMesh:
    """Mock service mesh"""
    async def get_global_mesh_analytics(self):
        return {"status": "mock", "services": 0}
    
    async def start_global_monitoring(self):
        pass


class MockAIManager:
    """Mock AI manager"""
    async def get_ai_system_overview(self):
        return {"status": "mock", "models": 0}


class MockSecurityManager:
    """Mock security manager"""
    async def initialize_security_system(self):
        pass
    
    async def start_continuous_monitoring(self):
        pass
    
    async def get_comprehensive_security_report(self):
        return {"status": "mock", "threats": 0}


class MockAnalyticsEngine:
    """Mock analytics engine"""
    async def get_business_intelligence_dashboard(self):
        return {"status": "mock", "metrics": 0}


# Create mock instances
api_cache_manager = MockCacheManager()
session_cluster = MockSessionCluster()
rate_limiter = MockRateLimiter()
db_cache_manager = MockCacheManager()
postgres_cache_manager = MockCacheManager()
mongodb_cache_manager = MockCacheManager()
event_sourcing_manager = MockEventSourcingManager()
grafana_cache_manager = MockCacheManager()
prometheus_cache_manager = MockCacheManager()
loki_cache_manager = MockCacheManager()
global_service_mesh = MockServiceMesh()
ultra_ai_manager = MockAIManager()
ultra_security_manager = MockSecurityManager()
ultra_analytics_engine = MockAnalyticsEngine()


# Mock event types
class EventType:
    """Mock event types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    SYSTEM_ERROR = "system_error"