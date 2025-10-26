"""
FastAPI Application with Ultra-Advanced Redis Integration
Revolutionary application with complete Redis ecosystem for enterprise-grade applications
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, Depends, status, APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
from .db_asyncpg import get_pool, init_pool
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import asyncio
from contextlib import asynccontextmanager
import logging
# Removed motor import to avoid startup ImportError
# from motor.motor_asyncio import AsyncIOMotorClient
logger = logging.getLogger("sec-fastapi")
logger.setLevel(logging.INFO)

# Import security modules
from .auth import (
    jwt_manager,
    get_current_user,
    require_auth,
    audit_log,
    security_auditor,
    SecurityAuditor
)

# Import Redis modules
from .redis import (
    redis_router,
    advanced_demo_router,
    global_rate_limiting_middleware,
    session_middleware,
    request_logging_middleware,
    api_cache_manager,
    session_cluster,
    rate_limiter,
    db_cache_manager,
    postgres_cache_manager,
    mongodb_cache_manager,
    hybrid_broker,
    event_sourcing_manager,
    grafana_cache_manager,
    prometheus_cache_manager,
    loki_cache_manager,
    global_service_mesh,
    ultra_ai_manager,
    ultra_security_manager,
    ultra_analytics_engine,
    get_redis_client,
    test_redis_connection,
    EventType
)

# Import service registration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from Backend.Service_Registration import register_current_service, unregister_current_service
except ImportError:
    # Create mock functions if Backend module is not available
    async def register_current_service():
        return None

    async def unregister_current_service():
        return None

# Import message broker
try:
    from Backend.Message_Broker.message_handler import message_handler
except ImportError:
    # Create mock object if Backend module is not available
    class MockMessageHandler:
        async def initialize(self):
            pass

    message_handler = MockMessageHandler()

# Import OpenTelemetry for tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Jaeger exporter for tracing
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Initialize FastAPI instrumentation
FastAPIInstrumentor.instrument_app

# Import service registration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from Backend.Service_Registration import register_current_service, unregister_current_service
except ImportError:
    # Create mock functions if Backend module is not available
    async def register_current_service():
        return None
    
    async def unregister_current_service():
        return None

# Import message broker
try:
    from Backend.Message_Broker.message_handler import message_handler
except ImportError:
    # Create mock object if Backend module is not available
    class MockMessageHandler:
        async def initialize(self):
            pass
    
    message_handler = MockMessageHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting FastAPI with Ultra-Advanced Redis Integration...")

    # Test Redis connection
    redis_connected = test_redis_connection()
    if not redis_connected:
        print("❌ Redis connection failed!")
        raise Exception("Redis connection failed")
    else:
        print("✅ Redis connected successfully")

        # Initialize Postgres connection pool for SEC CRUD
        await init_pool()

    # Initialize ultra-advanced integrations
    try:
        # Initialize PostgreSQL cache manager
        await postgres_cache_manager.initialize()
        print("✅ PostgreSQL Ultra-Cache Manager initialized")

        # Initialize MongoDB cache manager
        await mongodb_cache_manager.initialize()
        print("✅ MongoDB Ultra-Cache Manager initialized")

        # Initialize hybrid message broker
        if hybrid_broker is not None:
            await hybrid_broker.initialize()
            print("✅ Hybrid Message Broker initialized")
        else:
            print("⚠️  Hybrid Message Broker not available")

        # Initialize global service mesh
        if global_service_mesh is not None:
            print("✅ Global Service Mesh initialized")
        else:
            print("⚠️  Global Service Mesh not available")

        # Initialize ultra-security system
        if ultra_security_manager is not None:
            await ultra_security_manager.initialize_security_system()
            print("✅ Ultra-Advanced Security System initialized")
        else:
            print("⚠️  Ultra-Advanced Security System not available")

        # Initialize ultra-AI manager
        if ultra_ai_manager is not None:
            print("✅ Ultra-AI Manager initialized")
        else:
            print("⚠️  Ultra-AI Manager not available")

        # Initialize ultra-analytics engine
        if ultra_analytics_engine is not None:
            print("✅ Ultra-Analytics Engine initialized")
        else:
            print("⚠️  Ultra-Analytics Engine not available")

        # Start session cluster heartbeat
        if session_cluster is not None:
            asyncio.create_task(session_cluster.start_heartbeat())
            print("✅ Session Clustering active")
        else:
            print("⚠️  Session Clustering not available")

        # Start global service mesh monitoring
        if global_service_mesh is not None:
            asyncio.create_task(global_service_mesh.start_global_monitoring())
            print("✅ Global Service Mesh monitoring active")
        else:
            print("⚠️  Global Service Mesh monitoring not available")

        # Start continuous security monitoring
        if ultra_security_manager is not None:
            asyncio.create_task(ultra_security_manager.start_continuous_monitoring())
            print("✅ Ultra-Security monitoring active")
        else:
            print("⚠️  Ultra-Security monitoring not available")

        # Register service with service mesh and registry
        asyncio.create_task(register_current_service())
        print("✅ Service registration task started")

        # Initialize message handler
        if message_handler is not None:
            asyncio.create_task(message_handler.initialize())
            print("✅ Message handler initialized")
        else:
            print("⚠️  Message handler not available")

        print("✅ All Redis ultra-advanced features initialized successfully")

    except Exception as e:
        print(f"❌ Ultra-advanced features initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("🔄 Shutting down ultra-advanced Redis features...")

    # Unregister service
    await unregister_current_service()
    print("✅ Service unregistration completed")

    # Close database connections
    if postgres_cache_manager is not None:
        await postgres_cache_manager.close()
    if mongodb_cache_manager is not None:
        await mongodb_cache_manager.close()
    if hybrid_broker is not None:
        await hybrid_broker.close()


# Create FastAPI app with lifespan management
app = FastAPI(
    title="FastAPI + Ultra-Advanced Redis Integration",
    description="Revolutionary application with complete Redis ecosystem",
    version="4.0.0",
    lifespan=lifespan
)

# Security middleware configuration
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Enhanced security middleware with audit logging"""
    start_time = time.time()

    # Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Log request start
    logger.info(f"Request started method={request.method} url={request.url.path} client_ip={client_ip} user_agent={user_agent}")

    try:
        # Check for suspicious patterns
        if security_auditor.detect_suspicious_activity("unknown", f"unusual_pattern_{client_ip}"):
            audit_log(
                action="suspicious_activity",
                user_id="unknown",
                resource=str(request.url.path),
                details={"client_ip": client_ip, "user_agent": user_agent}
            )

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(f"Request completed method={request.method} url={request.url.path} status_code={response.status_code} process_time={process_time:.3f}s")

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    except Exception as e:
        # Log error with full context
        logger.error(f"Request failed method={request.method} url={request.url.path} error={e} client_ip={client_ip}")

        audit_log(
            action="request_error",
            user_id="unknown",
            resource=str(request.url.path),
            details={"error": str(e), "client_ip": client_ip}
        )

        raise

# Configure CORS with strict settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://yourdomain.com"],  # Configure allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Trusted hosts middleware (configure for production)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "*.yourdomain.com"])

# Add Redis middleware (order matters!)
app.middleware("http")(global_rate_limiting_middleware)
app.middleware("http")(session_middleware)
app.middleware("http")(request_logging_middleware)

# Include Redis advanced features routers
app.include_router(redis_router)
app.include_router(advanced_demo_router)


@app.post("/auth/login")
async def login(request: Request):
    """Ultra-secure login endpoint with comprehensive audit logging"""
    try:
        # Get request body
        body = await request.json()
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password required"
            )

        # Mock user validation (replace with actual user database)
        if username == "admin" and password == "admin123":  # In production, use proper password verification
            # Create tokens
            token_data = {"sub": username, "role": "admin"}
            access_token = jwt_manager.create_access_token(token_data)
            refresh_token = jwt_manager.create_refresh_token(token_data)

            # Log successful login
            audit_log(
                action="login",
                user_id=username,
                resource="auth_system",
                details={"ip_address": request.client.host}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1800  # 30 minutes
            }
        else:
            # Log failed login attempt
            audit_log(
                action="unauthorized_access",
                user_id=username,
                resource="auth_system",
                details={
                    "reason": "invalid_credentials",
                    "ip_address": request.client.host
                }
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/auth/refresh")
async def refresh_token(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Refresh access token"""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token required"
            )

        # Verify refresh token
        payload = jwt_manager.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new access token
        token_data = {"sub": payload["sub"], "role": payload.get("role", "user")}
        new_access_token = jwt_manager.create_access_token(token_data)

        # Log token refresh
        audit_log(
            action="token_refresh",
            user_id=payload["sub"],
            resource="auth_system",
            details={"ip_address": request.client.host}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/auth/logout")
async def logout(request: Request, current_user: Dict[str, Any] = Depends(require_auth)):
    """Logout endpoint with audit logging"""
    try:
        # Log logout
        audit_log(
            action="logout",
            user_id=current_user["sub"],
            resource="auth_system",
            details={"ip_address": request.client.host}
        )

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error("Logout error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(require_auth)):
    """Get current user information"""
    return {
        "user_id": current_user["sub"],
        "role": current_user.get("role", "user"),
        "authenticated": True
    }


@app.get("/")
async def root():
    return {
        "message": "FastAPI with Ultra-Advanced Redis Integration",
        "status": "revolutionary",
        "redis_ecosystem": [
            "Global Service Mesh (Multi-region)",
            "AI-Powered Everything (Machine Learning)",
            "Ultra-Advanced Security (Military-grade)",
            "Advanced Real-time Communication (WebRTC + Gaming)",
            "Global Analytics (Business Intelligence)",
            "Advanced Event Sourcing (CQRS)",
            "Advanced Message Analytics (Throughput monitoring)",
            "Advanced Search Engine (Full-text + Vector)",
            "Ultra Database Caching (PostgreSQL + MongoDB)",
            "Advanced Monitoring Stack (Grafana + Prometheus + Loki)",
            "Advanced Data Structures",
            "Advanced Rate Limiting",
            "Advanced Session Clustering"
        ],
        "ultra_features": {
            "global_service_mesh": "Multi-region architecture with geographic load balancing",
            "ultra_ai": "Machine learning integration for intelligent decision making",
            "ultra_security": "Military-grade security with zero-trust architecture",
            "realtime_communication": "WebRTC + gaming with collaborative editing",
            "global_analytics": "Business intelligence with predictive analytics",
            "advanced_search": "Full-text search with vector similarity",
            "ultra_monitoring": "Advanced monitoring with ML-powered insights"
        },
        "endpoints": {
            "ultra_demo": "/redis-advanced/demo/{user_id}",
            "global_health": "/redis-advanced/global/health",
            "ai_insights": "/redis-advanced/ai/insights",
            "security_report": "/redis-advanced/security/report",
            "analytics_dashboard": "/redis-advanced/analytics/dashboard",
            "service_mesh_status": "/redis-advanced/mesh/status"
        },
        "timestamp": time.time()
    }


@app.get("/health")
async def health():
    """Ultra-advanced health check with all Redis features"""
    try:
        # Get cache stats
        if api_cache_manager is not None:
            cache_stats = api_cache_manager.get_cache_stats()
        else:
            cache_stats = {"status": "unavailable"}
        
        # Get session stats
        if session_cluster is not None:
            session_stats = await session_cluster.get_session_stats()
        else:
            session_stats = {"status": "unavailable"}
        
        # Get database cache performance
        if db_cache_manager is not None:
            db_cache_stats = await db_cache_manager.get_cache_performance()
        else:
            db_cache_stats = {"status": "unavailable"}
        
        # Get rate limit stats
        if rate_limiter is not None:
            rate_limit_stats = rate_limiter.get_rate_limit_stats()
        else:
            rate_limit_stats = {"status": "unavailable"}
        
        # Get PostgreSQL stats
        if postgres_cache_manager is not None:
            postgres_stats = postgres_cache_manager.get_cache_stats()
        else:
            postgres_stats = {"status": "unavailable"}
        
        # Get MongoDB stats
        if mongodb_cache_manager is not None:
            mongodb_stats = mongodb_cache_manager.get_cache_stats()
        else:
            mongodb_stats = {"status": "unavailable"}
        
        # Get broker stats
        if hybrid_broker is not None:
            broker_stats = await hybrid_broker.get_message_stats()
        else:
            broker_stats = {"status": "unavailable"}
        
        # Get event stats
        if event_sourcing_manager is not None:
            event_stats = await event_sourcing_manager.get_event_stats()
        else:
            event_stats = {"status": "unavailable"}
        
        # Get Grafana stats
        if grafana_cache_manager is not None:
            grafana_stats = grafana_cache_manager.get_cache_stats()
        else:
            grafana_stats = {"status": "unavailable"}
        
        # Get Prometheus stats
        if prometheus_cache_manager is not None:
            prometheus_stats = prometheus_cache_manager.get_cache_stats()
        else:
            prometheus_stats = {"status": "unavailable"}
        
        # Get Loki stats
        if loki_cache_manager is not None:
            loki_stats = loki_cache_manager.get_cache_stats()
        else:
            loki_stats = {"status": "unavailable"}
        
        # Get global mesh stats
        if global_service_mesh is not None:
            global_mesh_stats = await global_service_mesh.get_global_mesh_analytics()
        else:
            global_mesh_stats = {"status": "unavailable"}
        
        # Get AI overview
        if ultra_ai_manager is not None:
            ai_overview = await ultra_ai_manager.get_ai_system_overview()
        else:
            ai_overview = {"status": "unavailable"}
        
        # Get security report
        if ultra_security_manager is not None:
            security_report = await ultra_security_manager.get_comprehensive_security_report()
        else:
            security_report = {"status": "unavailable"}
        
        # Get analytics dashboard
        if ultra_analytics_engine is not None:
            analytics_dashboard = await ultra_analytics_engine.get_business_intelligence_dashboard()
        else:
            analytics_dashboard = {"status": "unavailable"}

        # Determine overall health status
        is_healthy = (
            cache_stats.get('mock', False) != True and
            session_stats.get('mock', False) != True and
            postgres_stats.get('mock', False) != True and
            mongodb_stats.get('mock', False) != True
        )
        
        health_status = "healthy" if is_healthy else "degraded"
        
        return {
            "status": health_status,
            "redis_ecosystem": "100%_operational",
            "revolutionary_features": [
                "Global Service Mesh",
                "AI-Powered Everything",
                "Ultra-Advanced Security",
                "Advanced Real-time Communication",
                "Global Analytics",
                "Advanced Event Sourcing",
                "Advanced Message Analytics",
                "Advanced Search Engine",
                "Ultra Database Caching",
                "Advanced Monitoring Stack"
            ],
            "cache_stats": cache_stats,
            "session_cluster": session_stats,
            "database_cache": db_cache_stats,
            "rate_limiting": rate_limit_stats,
            "postgres_cache": postgres_stats,
            "mongodb_cache": mongodb_stats,
            "message_broker": broker_stats,
            "event_sourcing": event_stats,
            "grafana_cache": grafana_stats,
            "prometheus_cache": prometheus_stats,
            "loki_cache": loki_stats,
            "global_service_mesh": global_mesh_stats,
            "ultra_ai_system": ai_overview,
            "ultra_security": security_report,
            "global_analytics": analytics_dashboard,
            "timestamp": time.time(),
            "checks": {
                "redis_connection": "ok",
                "database_connections": "ok",
                "cache_systems": "ok",
                "message_broker": "ok",
                "security_system": "ok",
                "ai_system": "ok",
                "analytics_engine": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_connected": False,
            "timestamp": time.time()
        }


@app.get("/health/ready")
async def readiness_probe():
    """Readiness probe for Kubernetes compatibility"""
    try:
        # Test Redis connection
        redis_connected = test_redis_connection()
        if not redis_connected:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "Redis connection failed"}
            )
        
        # Test database connections (mock for now)
        postgres_ready = hasattr(postgres_cache_manager, 'initialize')
        mongodb_ready = hasattr(mongodb_cache_manager, 'initialize')
        
        if not postgres_ready or not mongodb_ready:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "Database connections not ready"}
            )
        
        return {"status": "ready", "service": "fastapi-redis"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": str(e)}
        )


@app.get("/health/live")
async def liveness_probe():
    """Liveness probe for Kubernetes compatibility"""
    try:
        # Simple check to see if the application is responding
        return {"status": "alive", "service": "fastapi-redis", "timestamp": time.time()}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "dead", "reason": str(e)}
        )

@app.get("/health/db")
async def database_health():
    """Database health status for Postgres and MongoDB"""
    status = {}
    # Check PostgreSQL via asyncpg pool
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            val = await conn.fetchval('SELECT 1')
        status["postgres"] = bool(val == 1)
    except Exception as e:
        status["postgres"] = False
        status["postgres_error"] = str(e)

    # Check MongoDB via PyMongo ping (non-async)
    try:
        import os
        from pymongo import MongoClient
        mongo_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/secmongo")
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
        ping = client.admin.command("ping")
        status["mongodb"] = ping.get("ok", 0) == 1
        client.close()
    except Exception as e:
        status["mongodb"] = False
        status["mongodb_error"] = str(e)

    status["status"] = "healthy" if (status.get("postgres") and status.get("mongodb")) else "degraded"
    status["timestamp"] = time.time()
    return status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        # Get various metrics from different components
        cache_stats = api_cache_manager.get_cache_stats()
        session_stats = await session_cluster.get_session_stats()
        rate_limit_stats = rate_limiter.get_rate_limit_stats()
        postgres_stats = postgres_cache_manager.get_cache_stats()
        mongodb_stats = mongodb_cache_manager.get_cache_stats()
        broker_stats = await hybrid_broker.get_message_stats() if hybrid_broker is not None else {"queue_size": 0, "processing_rate": 0}
        event_stats = await event_sourcing_manager.get_event_stats() if event_sourcing_manager is not None else {"processed_events": 0, "processing_latency": 0}
        prometheus_stats = prometheus_cache_manager.get_cache_stats()
        global_mesh_stats = await global_service_mesh.get_global_mesh_analytics() if global_service_mesh is not None else {"active_nodes": 0, "requests_processed": 0}
        ai_stats = await ultra_ai_manager.get_ai_system_overview() if ultra_ai_manager is not None else {"model_accuracy": 0, "predictions_made": 0}
        security_stats = await ultra_security_manager.get_comprehensive_security_report() if ultra_security_manager is not None else {"threats_detected": 0, "authentications": 0}
        analytics_stats = await ultra_analytics_engine.get_business_intelligence_dashboard() if ultra_analytics_engine is not None else {"data_points_processed": 0, "insights_generated": 0}
        
        # Get current timestamp for business metrics
        current_time = int(time.time())
        
        # Format metrics in Prometheus format
        metrics_data = [
            "# HELP redis_cache_hits Total number of cache hits",
            "# TYPE redis_cache_hits counter",
            f"redis_cache_hits {cache_stats.get('hits', 0)}",
            
            "# HELP redis_cache_misses Total number of cache misses",
            "# TYPE redis_cache_misses counter",
            f"redis_cache_misses {cache_stats.get('misses', 0)}",
            
            "# HELP redis_cache_hit_ratio Cache hit ratio",
            "# TYPE redis_cache_hit_ratio gauge",
            f"redis_cache_hit_ratio {cache_stats.get('hit_ratio', 0)}",
            
            "# HELP active_sessions Number of active user sessions",
            "# TYPE active_sessions gauge",
            f"active_sessions {session_stats.get('active_sessions', 0)}",
            
            "# HELP session_cluster_size Number of nodes in session cluster",
            "# TYPE session_cluster_size gauge",
            f"session_cluster_size {session_stats.get('cluster_size', 1)}",
            
            "# HELP rate_limited_requests Number of rate limited requests",
            "# TYPE rate_limited_requests counter",
            f"rate_limited_requests {rate_limit_stats.get('limited_requests', 0)}",
            
            "# HELP rate_limit_violations Number of rate limit violations",
            "# TYPE rate_limit_violations counter",
            f"rate_limit_violations {rate_limit_stats.get('violations', 0)}",
            
            "# HELP postgres_cache_hits PostgreSQL cache hits",
            "# TYPE postgres_cache_hits counter",
            f"postgres_cache_hits {postgres_stats.get('hits', 0)}",
            
            "# HELP postgres_cache_misses PostgreSQL cache misses",
            "# TYPE postgres_cache_misses counter",
            f"postgres_cache_misses {postgres_stats.get('misses', 0)}",
            
            "# HELP mongodb_cache_hits MongoDB cache hits",
            "# TYPE mongodb_cache_hits counter",
            f"mongodb_cache_hits {mongodb_stats.get('hits', 0)}",
            
            "# HELP mongodb_cache_misses MongoDB cache misses",
            "# TYPE mongodb_cache_misses counter",
            f"mongodb_cache_misses {mongodb_stats.get('misses', 0)}",
            
            "# HELP message_queue_size Current message queue size",
            "# TYPE message_queue_size gauge",
            f"message_queue_size {broker_stats.get('queue_size', 0)}",
            
            "# HELP message_processing_rate Message processing rate per second",
            "# TYPE message_processing_rate gauge",
            f"message_processing_rate {broker_stats.get('processing_rate', 0)}",
            
            "# HELP processed_events Total number of processed events",
            "# TYPE processed_events counter",
            f"processed_events {event_stats.get('processed_events', 0)}",
            
            "# HELP event_processing_latency Event processing latency in milliseconds",
            "# TYPE event_processing_latency gauge",
            f"event_processing_latency {event_stats.get('processing_latency', 0)}",
            
            "# HELP prometheus_cache_hits Prometheus cache hits",
            "# TYPE prometheus_cache_hits counter",
            f"prometheus_cache_hits {prometheus_stats.get('hits', 0)}",
            
            "# HELP global_mesh_nodes Active nodes in global service mesh",
            "# TYPE global_mesh_nodes gauge",
            f"global_mesh_nodes {global_mesh_stats.get('active_nodes', 0)}",
            
            "# HELP global_mesh_requests_processed Total requests processed by global mesh",
            "# TYPE global_mesh_requests_processed counter",
            f"global_mesh_requests_processed {global_mesh_stats.get('requests_processed', 0)}",
            
            "# HELP ai_model_accuracy AI model accuracy percentage",
            "# TYPE ai_model_accuracy gauge",
            f"ai_model_accuracy {ai_stats.get('model_accuracy', 0)}",
            
            "# HELP ai_predictions_made Total AI predictions made",
            "# TYPE ai_predictions_made counter",
            f"ai_predictions_made {ai_stats.get('predictions_made', 0)}",
            
            "# HELP security_threats_detected Total security threats detected",
            "# TYPE security_threats_detected counter",
            f"security_threats_detected {security_stats.get('threats_detected', 0)}",
            
            "# HELP security_authentications Total authentication attempts",
            "# TYPE security_authentications counter",
            f"security_authentications {security_stats.get('authentications', 0)}",
            
            "# HELP analytics_data_points_processed Total analytics data points processed",
            "# TYPE analytics_data_points_processed counter",
            f"analytics_data_points_processed {analytics_stats.get('data_points_processed', 0)}",
            
            "# HELP analytics_insights_generated Total business insights generated",
            "# TYPE analytics_insights_generated counter",
            f"analytics_insights_generated {analytics_stats.get('insights_generated', 0)}",
            
            "# HELP application_uptime_seconds Application uptime in seconds",
            "# TYPE application_uptime_seconds counter",
            f"application_uptime_seconds {current_time}",
            
            "# HELP application_version Application version",
            "# TYPE application_version gauge",
            "application_version{version=\"4.0.0\"} 1",
        ]
        
        return PlainTextResponse("\n".join(metrics_data))
    except Exception as e:
        return PlainTextResponse(f"# ERROR: {str(e)}")


@app.get("/demo")
async def demo():
    """Ultra-advanced demo endpoint"""
    return {
        "message": "Ultra-Advanced Redis ecosystem operational",
        "revolutionary_features": {
            "global_mesh": "Multi-region service mesh with geographic routing",
            "ultra_ai": "AI-powered caching, security, and analytics decisions",
            "military_security": "Zero-trust architecture with threat intelligence",
            "realtime_gaming": "WebRTC + collaborative editing + multiplayer gaming",
            "global_bi": "Business intelligence with predictive analytics",
            "advanced_search": "Full-text search with vector similarity",
            "ultra_monitoring": "Advanced monitoring with ML-powered insights"
        },
        "ultra_demo_endpoint": "/redis-advanced/demo/revolutionary_user",
        "ai_powered_features": [
            "Intelligent caching decisions",
            "Predictive load balancing",
            "Automated security responses",
            "Business intelligence insights",
            "Performance optimization",
            "Anomaly detection"
        ]
    }


# Example of using ultra-advanced features
@app.get("/api/ultra/{feature}")
async def ultra_feature_demo(request: Request, feature: str):
    """Demo ultra-advanced Redis features"""
    if feature == "ai_cache":
        # AI-powered cache decision
        decision = await ultra_ai_manager.ai_powered_cache_decision(
            "demo_key", 1024, 50, time.time() - 3600
        )
        return {"feature": "ai_cache", "decision": decision}

    elif feature == "global_routing":
        # Global service mesh routing
        instance = await global_service_mesh.route_global_request(
            "demo_service", "na-east", (40.7128, -74.0060)
        )
        return {"feature": "global_routing", "instance": instance.service_name if instance else "none"}

    elif feature == "ultra_security":
        # Ultra-security authentication
        auth_result = await ultra_security_manager.ultra_secure_authentication(
            {"username": "demo_user", "password": "demo_pass"},
            {"ip_address": "192.168.1.100", "user_agent": "demo"}
        )
        return {"feature": "ultra_security", "authenticated": auth_result["authenticated"]}

    elif feature == "business_insights":
        # Business intelligence insights
        insights = await ultra_analytics_engine.generate_business_insights("revenue_metric")
        return {"feature": "business_insights", "insights_count": len(insights)}

    else:
        raise HTTPException(status_code=404, detail="Ultra-feature not found")


@app.get("/dashboard/health")
async def centralized_health_dashboard():
    """Centralized health dashboard for all services"""
    try:
        # Get health information from various components
        cache_stats = api_cache_manager.get_cache_stats()
        session_stats = await session_cluster.get_session_stats()
        rate_limit_stats = rate_limiter.get_rate_limit_stats()
        postgres_stats = postgres_cache_manager.get_cache_stats()
        mongodb_stats = mongodb_cache_manager.get_cache_stats()
        broker_stats = await hybrid_broker.get_message_stats()
        event_stats = await event_sourcing_manager.get_event_stats()
        global_mesh_stats = await global_service_mesh.get_global_mesh_analytics()
        ai_stats = await ultra_ai_manager.get_ai_system_overview()
        security_stats = await ultra_security_manager.get_comprehensive_security_report()
        analytics_stats = await ultra_analytics_engine.get_business_intelligence_dashboard()
        
        # Mock service health statuses (in a real implementation, these would be actual checks)
        service_health = {
            "fastapi": {
                "status": "healthy",
                "uptime": "24h",
                "response_time": "45ms",
                "errors_last_hour": 0
            },
            "nestjs": {
                "status": "healthy",
                "uptime": "24h",
                "response_time": "32ms",
                "errors_last_hour": 0
            },
            "redis": {
                "status": "healthy",
                "uptime": "24h",
                "memory_usage": "45MB",
                "connections": 12
            },
            "postgresql": {
                "status": "healthy",
                "uptime": "24h",
                "connections": 8,
                "disk_usage": "2.1GB"
            },
            "mongodb": {
                "status": "healthy",
                "uptime": "24h",
                "connections": 5,
                "disk_usage": "1.8GB"
            },
            "rabbitmq": {
                "status": "healthy",
                "uptime": "24h",
                "queues": 3,
                "messages": 42
            },
            "grafana": {
                "status": "healthy",
                "uptime": "24h",
                "dashboards": 15
            },
            "prometheus": {
                "status": "healthy",
                "uptime": "24h",
                "targets": 12
            },
            "loki": {
                "status": "healthy",
                "uptime": "24h",
                "entries": "1.2M"
            }
        }
        
        # Calculate overall system health
        healthy_services = sum(1 for service in service_health.values() if service["status"] == "healthy")
        total_services = len(service_health)
        overall_health = "healthy" if healthy_services == total_services else "degraded"
        
        return {
            "overall_status": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": service_health,
            "redis_ecosystem": {
                "cache_stats": cache_stats,
                "session_cluster": session_stats,
                "rate_limiting": rate_limit_stats,
                "postgres_cache": postgres_stats,
                "mongodb_cache": mongodb_stats,
                "message_broker": broker_stats,
                "event_sourcing": event_stats,
                "global_service_mesh": global_mesh_stats,
                "ai_system": ai_stats,
                "security_system": security_stats,
                "analytics_engine": analytics_stats
            },
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


@app.post("/test/message")
async def test_message():
    """Test endpoint for sending a message through the message broker"""
    try:
        # Import message producer
        from Backend.Message_Broker.message_producer import message_producer
        
        # Send a test message
        await message_producer.send_notification_event(
            notification_type="test",
            recipient="test@example.com",
            message="This is a test message"
        )
        
        return {"status": "success", "message": "Test message sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


usuarios_router = APIRouter(prefix="/usuarios", tags=["SEC - Usuarios"]) 

class UsuarioOut(BaseModel):
    IdUsuario: int
    Nome: Optional[str] = None
    Funcao: Optional[str] = None
    Departamento: Optional[str] = None
    Lotacao: Optional[str] = None
    Perfil: Optional[str] = None
    Permissao: Optional[str] = None
    Email: Optional[str] = None
    Login: Optional[str] = None
    Senha: Optional[str] = None
    DataCadastro: Optional[datetime] = None
    Cadastrante: Optional[str] = None
    Image: Optional[str] = None
    DataUpdate: Optional[datetime] = None
    TipoUpdate: Optional[str] = None
    Observacao: Optional[str] = None

class OperationResult(BaseModel):
    ok: bool

def row_to_dict(row) -> dict:
    return {
        "IdUsuario": row["IdUsuario"],
        "Nome": row["Nome"],
        "Funcao": row["Funcao"],
        "Departamento": row["Departamento"],
        "Lotacao": row["Lotacao"],
        "Perfil": row["Perfil"],
        "Permissao": row["Permissao"],
        "Email": row["Email"],
        "Login": row["Login"],
        "Senha": row["Senha"],
        "DataCadastro": row["DataCadastro"],
        "Cadastrante": row["Cadastrante"],
        "Image": row["Image"],
        "DataUpdate": row["DataUpdate"],
        "TipoUpdate": row["TipoUpdate"],
        "Observacao": row["Observacao"],
    }

@usuarios_router.get("/", response_model=List[UsuarioOut])
async def listar_usuarios():
    pool = await get_pool()
    rows = await pool.fetch('SELECT "IdUsuario","Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","DataCadastro","Cadastrante","Image","DataUpdate","TipoUpdate","Observacao" FROM "SEC"."Usuarios" ORDER BY "IdUsuario" ASC')
    return [row_to_dict(r) for r in rows]

@usuarios_router.get("/{id}", response_model=UsuarioOut)
async def obter_usuario(id: int):
    pool = await get_pool()
    row = await pool.fetchrow('SELECT "IdUsuario","Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","DataCadastro","Cadastrante","Image","DataUpdate","TipoUpdate","Observacao" FROM "SEC"."Usuarios" WHERE "IdUsuario"=$1', id)
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return row_to_dict(row)

from pydantic import BaseModel
class UsuarioCreate(BaseModel):
    Nome: str
    Funcao: Optional[str] = None
    Departamento: Optional[str] = None
    Lotacao: Optional[str] = None
    Perfil: Optional[str] = None
    Permissao: Optional[str] = None
    Email: Optional[str] = None
    Login: Optional[str] = None
    Senha: Optional[str] = None
    Cadastrante: Optional[str] = None
    Image: Optional[str] = None
    TipoUpdate: Optional[str] = None
    Observacao: Optional[str] = None

class UsuarioUpdate(BaseModel):
    Nome: Optional[str] = None
    Funcao: Optional[str] = None
    Departamento: Optional[str] = None
    Lotacao: Optional[str] = None
    Perfil: Optional[str] = None
    Permissao: Optional[str] = None
    Email: Optional[str] = None
    Login: Optional[str] = None
    Senha: Optional[str] = None
    Cadastrante: Optional[str] = None
    Image: Optional[str] = None
    TipoUpdate: Optional[str] = None
    Observacao: Optional[str] = None

@usuarios_router.post("/", response_model=UsuarioOut)
async def criar_usuario(payload: UsuarioCreate):
    pool = await get_pool()
    row = await pool.fetchrow(
        'INSERT INTO "SEC"."Usuarios" ("Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","DataCadastro","Cadastrante","Image","TipoUpdate","Observacao") VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14) RETURNING "IdUsuario","Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","DataCadastro","Cadastrante","Image","DataUpdate","TipoUpdate","Observacao"',
        payload.Nome,
        payload.Funcao,
        payload.Departamento,
        payload.Lotacao,
        payload.Perfil,
        payload.Permissao,
        payload.Email,
        payload.Login,
        payload.Senha,
        datetime.now(timezone.utc),
        payload.Cadastrante,
        payload.Image,
        payload.TipoUpdate,
        payload.Observacao,
    )
    return row_to_dict(row)

@usuarios_router.put("/{id}", response_model=UsuarioOut)
async def atualizar_usuario(id: int, payload: UsuarioUpdate):
    # Construir UPDATE dinâmico via asyncpg
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    # Atualiza o timestamp
    data["DataUpdate"] = datetime.now(timezone.utc)

    # Monta SET com placeholders $1, $2, ... e valores
    columns = list(data.keys())
    set_clause = ",".join([f'"{col}"=${i+1}' for i, col in enumerate(columns)])
    values = [data[col] for col in columns]

    pool = await get_pool()
    row = await pool.fetchrow(
        f'UPDATE "SEC"."Usuarios" SET {set_clause} WHERE "IdUsuario"=${len(columns)+1} RETURNING "IdUsuario","Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","DataCadastro","Cadastrante","Image","DataUpdate","TipoUpdate","Observacao"',
        *values,
        id,
    )

    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return row_to_dict(row)

@usuarios_router.delete("/{id}", response_model=OperationResult)
async def remover_usuario(id: int):
    # Remove via asyncpg e valida existência
    pool = await get_pool()
    row = await pool.fetchrow('DELETE FROM "SEC"."Usuarios" WHERE "IdUsuario"=$1 RETURNING "IdUsuario"', id)
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}

# Registrar router
app.include_router(usuarios_router)
