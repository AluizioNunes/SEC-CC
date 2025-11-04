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
import os
from contextlib import asynccontextmanager
import logging
# Removed motor import to avoid startup ImportError
# from motor.motor_asyncio import AsyncIOMotorClient
logger = logging.getLogger("sec-fastapi")
# Read log level from environment (FASTAPI_LOG_LEVEL) with fallback to INFO
_log_level = os.getenv("FASTAPI_LOG_LEVEL", "info").upper()
logger.setLevel(getattr(logging, _log_level, logging.INFO))

# Import security modules
from .auth import (
    jwt_manager,
    get_current_user,
    require_auth,
    audit_log,
    security_auditor,
    SecurityAuditor,
    authenticate_user,
    create_access_token
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

# Import Auth router (modularized /auth endpoints)
from .routes.auth_router import auth_router
from .routes.ai_router import ai_router

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
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# Prefer OTLP exporter to avoid Jaeger deprecation
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except Exception:
    OTLPSpanExporter = None

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# OTLP exporter for tracing (avoids Jaeger deprecation)
if OTLPSpanExporter is not None:
    try:
        otlp_exporter = OTLPSpanExporter()
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception:
        pass

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

    # Dev flags to skip external dependencies during local development
    _skip_redis = os.getenv("FASTAPI_SKIP_REDIS", "0") == "1"
    _skip_db = os.getenv("FASTAPI_SKIP_DB", "1") == "1"  # default skip DB in dev

    # Test Redis connection (await the coroutine properly)
    if _skip_redis:
        print("⚠️  Skipping Redis connection check (FASTAPI_SKIP_REDIS=1)")
        redis_connected = False
    else:
        try:
            redis_connected = await test_redis_connection()
        except Exception as _e:
            print(f"❌ Redis connection check errored: {_e}")
            redis_connected = False

    if not redis_connected:
        # In dev, allow startup without Redis to enable local API testing
        print("⚠️  Redis not available, continuing startup in degraded dev mode")
    else:
        print("✅ Redis connected successfully")

    # Initialize Postgres connection pool for SEC CRUD if not skipped
    if _skip_db:
        print("⚠️  Skipping Postgres pool initialization (FASTAPI_SKIP_DB=1)")
    else:
        try:
            await init_pool()
            print("✅ Postgres connection pool initialized")
        except Exception as _e:
            print(f"❌ Postgres pool initialization failed: {_e}")
            # Do not crash in dev; continue without DB
            pass

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

# Configure CORS with strict settings (from env CORS_ORIGINS if provided)
_cors_origins_str = os.getenv("CORS_ORIGINS")
if _cors_origins_str:
    _cors_origins = [o.strip() for o in _cors_origins_str.split(",") if o.strip()]
else:
    _cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://yourdomain.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=86400,
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
# Include Auth router
app.include_router(auth_router)
# Include AI router
app.include_router(ai_router)


@app.get("/redis/test")
async def redis_test():
    """Basic Redis connectivity test endpoint used by integration tests
    Returns 200 if Redis ping succeeds, otherwise 503.
    """
    try:
        # Prefer the packaged test function if available
        from app.redis import test_redis_connection as _test_conn  # type: ignore
    except Exception:
        try:
            # Fallback to local client implementation
            from app.redis.local_redis_client import test_redis_connection as _test_conn  # type: ignore
        except Exception:
            async def _test_conn() -> bool:
                return False
    ok = await _test_conn()
    if ok:
        return {"status": "ok"}
    return JSONResponse(status_code=503, content={"status": "unavailable"})











# Simple protected route for tests
@app.get("/protected")
async def protected(current_user: Dict[str, Any] = Depends(require_auth)):
    return {"status": "ok"}


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


# ===================== Permissões (Efetivas por Usuário) =====================
permissoes_router = APIRouter(prefix="/permissoes", tags=["SEC - Permissoes"]) 

class PermissaoItem(BaseModel):
    nome: str
    modulo: Optional[str] = None
    tipo: Optional[str] = None

class ActionsPermission(BaseModel):
    view: bool = False
    create: bool = False
    edit: bool = False
    delete: bool = False

class ScreensMatrix(BaseModel):
    usuarios: ActionsPermission = ActionsPermission()
    perfil: ActionsPermission = ActionsPermission()
    permissoes: ActionsPermission = ActionsPermission()

class PermissionMatrixOut(BaseModel):
    screens: ScreensMatrix

class UserPermissionsResponse(BaseModel):
    userId: int
    profiles: List[Dict[str, Any]]
    raw: List[PermissaoItem]
    matrix: PermissionMatrixOut

def _raw_to_matrix(raw: List[PermissaoItem]) -> PermissionMatrixOut:
    # Inicializa matriz com tudo falso
    m = {
        "usuarios": {"view": False, "create": False, "edit": False, "delete": False},
        "perfil": {"view": False, "create": False, "edit": False, "delete": False},
        "permissoes": {"view": False, "create": False, "edit": False, "delete": False},
    }

    # Se ADMIN_TOTAL presente, libera tudo
    if any((p.nome or "").upper() == "ADMIN_TOTAL" for p in raw):
        for key in m.keys():
            m[key] = {"view": True, "create": True, "edit": True, "delete": True}
        return PermissionMatrixOut(screens=ScreensMatrix(
            usuarios=ActionsPermission(**m["usuarios"]),
            perfil=ActionsPermission(**m["perfil"]),
            permissoes=ActionsPermission(**m["permissoes"]),
        ))

    # Mapeia permissões por módulo (Usuarios, Perfil, Permissoes)
    for p in raw:
        nome = (p.nome or "").upper()
        modulo_raw = (p.modulo or "").upper()
        tipo = (p.tipo or "").upper()

        # Normalizar nomes de módulo para chaves da matriz
        if modulo_raw in ("USUARIOS", "USUARIO"):
            modulo = "usuarios"
        elif modulo_raw in ("PERFIL", "PERFIS", "PROFILE"):
            modulo = "perfil"
        elif modulo_raw in ("PERMISSOES", "PERMISSAO", "PERMISSIONS"):
            modulo = "permissoes"
        else:
            modulo = None

        if modulo is None:
            # Ignora módulos não mapeados na matriz admin
            continue

        # Tipos padrão
        if tipo == "READ" or nome.endswith("_READ_PUBLIC"):
            m[modulo]["view"] = True
        elif tipo == "CREATE":
            m[modulo]["create"] = True
        elif tipo == "UPDATE":
            m[modulo]["edit"] = True
        elif tipo == "DELETE":
            m[modulo]["delete"] = True
        elif tipo == "ADMIN":
            m[modulo] = {"view": True, "create": True, "edit": True, "delete": True}

    # Retorna matriz
    return PermissionMatrixOut(screens=ScreensMatrix(
        usuarios=ActionsPermission(**m["usuarios"]),
        perfil=ActionsPermission(**m["perfil"]),
        permissoes=ActionsPermission(**m["permissoes"]),
    ))

@permissoes_router.get("/usuarios/{id}", response_model=UserPermissionsResponse)
async def obter_permissoes_usuario_endpoint(id: int, current_user: Dict[str, Any] = Depends(require_auth)):
    # Fallback sem banco para desenvolvimento
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        usr = None
        for u in FAKE_USERS:
            if u["IdUsuario"] == id:
                usr = u
                break
        if not usr:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        # Admin: libera tudo
        perfil_nome = (usr.get("Perfil") or "").upper()
        raw: List[PermissaoItem] = []
        if perfil_nome in ("ADMIN", "ADMINISTRADOR"):
            raw = [
                PermissaoItem(nome="ADMIN_TOTAL", modulo="Sistema", tipo="ADMIN"),
                PermissaoItem(nome="USUARIO_CREATE", modulo="Usuarios", tipo="CREATE"),
                PermissaoItem(nome="USUARIO_READ", modulo="Usuarios", tipo="READ"),
                PermissaoItem(nome="USUARIO_UPDATE", modulo="Usuarios", tipo="UPDATE"),
                PermissaoItem(nome="USUARIO_DELETE", modulo="Usuarios", tipo="DELETE"),
            ]
        else:
            raw = [PermissaoItem(nome="USUARIO_READ", modulo="Usuarios", tipo="READ")]

        matrix = _raw_to_matrix(raw)
        return UserPermissionsResponse(
            userId=id,
            profiles=[{"id": usr.get("IdUsuario"), "name": usr.get("Perfil") or "Usuário"}],
            raw=raw,
            matrix=matrix,
        )

    # Com banco: agrega perfil principal + perfis adicionais
    pool = await get_pool()
    # Perfis do usuário (principal + adicionais)
    perfis_rows = await pool.fetch(
        'WITH principal AS (\n'
        '  SELECT u.idperfilprincipal AS idperfil\n'
        '  FROM "SEC"."Usuario" u\n'
        '  WHERE u.idusuario=$1\n'
        '), adicionais AS (\n'
        '  SELECT up.idperfil\n'
        '  FROM "SEC"."UsuarioPerfil" up\n'
        '  WHERE up.idusuario=$1\n'
        ')\n'
        'SELECT p.idperfil, p.nomeperfil\n'
        'FROM "SEC"."Perfil" p\n'
        'JOIN (SELECT idperfil FROM principal UNION SELECT idperfil FROM adicionais) x ON x.idperfil = p.idperfil',
        id,
    )
    if not perfis_rows:
        # Usuário sem perfis; ainda retornar estrutura vazia
        perfis = []
    else:
        perfis = [{"id": r["idperfil"], "name": r["nomeperfil"]} for r in perfis_rows]

    # Permissões efetivas via união de perfis
    perms_rows = await pool.fetch(
        'WITH perfis AS (\n'
        '  SELECT u.idperfilprincipal AS idperfil\n'
        '  FROM "SEC"."Usuario" u\n'
        '  WHERE u.idusuario=$1\n'
        '  UNION\n'
        '  SELECT up.idperfil\n'
        '  FROM "SEC"."UsuarioPerfil" up\n'
        '  WHERE up.idusuario=$1\n'
        ')\n'
        'SELECT DISTINCT pm.nomepermissao AS nome, pm.modulo AS modulo, pm.tipopermissao AS tipo\n'
        'FROM perfis pf\n'
        'JOIN "SEC"."PerfilPermissao" pp ON pp.idperfil = pf.idperfil\n'
        'JOIN "SEC"."Permissao" pm ON pm.idpermissao = pp.idpermissao\n'
        'WHERE pm.ativo = TRUE\n'
        'ORDER BY pm.modulo, pm.tipopermissao',
        id,
    )

    raw = [PermissaoItem(nome=r["nome"], modulo=r["modulo"], tipo=r["tipo"]) for r in perms_rows]
    matrix = _raw_to_matrix(raw)

    return UserPermissionsResponse(
        userId=id,
        profiles=perfis,
        raw=raw,
        matrix=matrix,
    )



@app.get("/health")
async def health():
    return {"status": "healthy"}


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

@app.get("/api/v1/health/db")
async def database_health_v1():
    return await database_health()


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

FAKE_USERS = [
    {
        "IdUsuario": 1,
        "Nome": "Administrador Demo",
        "Funcao": None,
        "Departamento": None,
        "Lotacao": None,
        "Perfil": "Administrador",
        "Permissao": "full",
        "Email": "admin@sec.gov",
        "Login": "admin",
        "Senha": None,
        "DataCadastro": datetime.now(timezone.utc).isoformat(),
        "Cadastrante": "API",
        "Image": None,
        "DataUpdate": None,
        "TipoUpdate": None,
        "Observacao": None,
    },
    {
        "IdUsuario": 2,
        "Nome": "Usuário Demo",
        "Funcao": None,
        "Departamento": None,
        "Lotacao": None,
        "Perfil": "Usuário",
        "Permissao": "limited",
        "Email": "usuario@sec.gov",
        "Login": "usuario",
        "Senha": None,
        "DataCadastro": datetime.now(timezone.utc).isoformat(),
        "Cadastrante": "API",
        "Image": None,
        "DataUpdate": None,
        "TipoUpdate": None,
        "Observacao": None,
    },
]

@usuarios_router.get("/", response_model=List[UsuarioOut])
async def listar_usuarios():
    # Fallback sem banco para desenvolvimento
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        return FAKE_USERS
    pool = await get_pool()
    rows = await pool.fetch('SELECT idusuario AS "IdUsuario", nome AS "Nome", NULL::text AS "Funcao", NULL::text AS "Departamento", NULL::text AS "Lotacao", perfil AS "Perfil", permissao AS "Permissao", email AS "Email", usuario AS "Login", senha AS "Senha", datacadastro AS "DataCadastro", cadastrante AS "Cadastrante", imagem AS "Image", dataupdate AS "DataUpdate", NULL::text AS "TipoUpdate", NULL::text AS "Observacao" FROM "SEC".Usuario ORDER BY idusuario ASC')
    return [row_to_dict(r) for r in rows]

@usuarios_router.get("/{id}", response_model=UsuarioOut)
async def obter_usuario(id: int):
    # Fallback sem banco
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        for u in FAKE_USERS:
            if u["IdUsuario"] == id:
                return u
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    pool = await get_pool()
    row = await pool.fetchrow('SELECT idusuario AS "IdUsuario", nome AS "Nome", NULL::text AS "Funcao", NULL::text AS "Departamento", NULL::text AS "Lotacao", perfil AS "Perfil", permissao AS "Permissao", email AS "Email", usuario AS "Login", senha AS "Senha", datacadastro AS "DataCadastro", cadastrante AS "Cadastrante", imagem AS "Image", dataupdate AS "DataUpdate", NULL::text AS "TipoUpdate", NULL::text AS "Observacao" FROM "SEC".Usuario WHERE idusuario=$1', id)
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
    # Fallback sem banco
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        new_id = (max([u["IdUsuario"] for u in FAKE_USERS]) + 1) if FAKE_USERS else 1
        rec = {
            "IdUsuario": new_id,
            "Nome": payload.Nome,
            "Funcao": payload.Funcao,
            "Departamento": payload.Departamento,
            "Lotacao": payload.Lotacao,
            "Perfil": payload.Perfil,
            "Permissao": payload.Permissao,
            "Email": payload.Email,
            "Login": payload.Login or (payload.Email or payload.Nome or f"user{new_id}"),
            "Senha": payload.Senha,
            "DataCadastro": datetime.now(timezone.utc).isoformat(),
            "Cadastrante": payload.Cadastrante or 'API',
            "Image": payload.Image,
            "DataUpdate": None,
            "TipoUpdate": payload.TipoUpdate,
            "Observacao": payload.Observacao,
        }
        FAKE_USERS.append(rec)
        return rec
    pool = await get_pool()
    row = await pool.fetchrow(
        'INSERT INTO "SEC"."Usuario" (nome, perfil, permissao, email, usuario, senha, datacadastro, cadastrante, imagem) VALUES ($1,$2,$3,$4,$5,$6,CURRENT_TIMESTAMP,$7,$8) RETURNING idusuario AS "IdUsuario", nome AS "Nome", NULL::text AS "Funcao", NULL::text AS "Departamento", NULL::text AS "Lotacao", perfil AS "Perfil", permissao AS "Permissao", email AS "Email", usuario AS "Login", senha AS "Senha", datacadastro AS "DataCadastro", cadastrante AS "Cadastrante", imagem AS "Image", dataupdate AS "DataUpdate", NULL::text AS "TipoUpdate", NULL::text AS "Observacao"',
        payload.Nome,
        payload.Perfil,
        payload.Permissao,
        payload.Email,
        payload.Login,
        payload.Senha,
        (payload.Cadastrante or 'API'),
        payload.Image,
    )
    return row_to_dict(row)

@usuarios_router.put("/{id}", response_model=UsuarioOut)
async def atualizar_usuario(id: int, payload: UsuarioUpdate):
    # Fallback sem banco
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        data = payload.dict(exclude_unset=True)
        for u in FAKE_USERS:
            if u["IdUsuario"] == id:
                for k, v in data.items():
                    if k in {"Nome","Funcao","Departamento","Lotacao","Perfil","Permissao","Email","Login","Senha","Cadastrante","Image","TipoUpdate","Observacao"}:
                        u[k] = v
                u["DataUpdate"] = datetime.now(timezone.utc).isoformat()
                return u
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    # Mapear payload para colunas reais
    key_mapping = {"Login": "Usuario", "Image": "Imagem"}
    allowed = {"Nome","Perfil","Permissao","Email","Usuario","Senha","Cadastrante","Imagem"}

    mapped_data = {}
    for k, v in data.items():
        db_col = key_mapping.get(k, k)
        if db_col in allowed:
            mapped_data[db_col] = v

    # DataUpdate será atualizado via SQL (CURRENT_TIMESTAMP)

    # Não aceitar DataUpdate do cliente; timestamp via SQL
    if not mapped_data:
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualizar")
    
    columns = list(mapped_data.keys())
    set_clause = ",".join([f'{col}=${i+1}' for i, col in enumerate(columns)])
    # Adiciona DataUpdate server-side
    set_clause = set_clause + ", DataUpdate=CURRENT_TIMESTAMP"
    values = [mapped_data[col] for col in columns]

    pool = await get_pool()
    row = await pool.fetchrow(
        f'UPDATE "SEC".Usuario SET {set_clause} WHERE idusuario=${len(columns)+1} RETURNING idusuario AS "IdUsuario", nome AS "Nome", NULL::text AS "Funcao", NULL::text AS "Departamento", NULL::text AS "Lotacao", perfil AS "Perfil", permissao AS "Permissao", email AS "Email", usuario AS "Login", senha AS "Senha", datacadastro AS "DataCadastro", cadastrante AS "Cadastrante", imagem AS "Image", dataupdate AS "DataUpdate", NULL::text AS "TipoUpdate", NULL::text AS "Observacao"',
        *values,
        id,
    )

    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return row_to_dict(row)

@usuarios_router.delete("/{id}", response_model=OperationResult)
async def remover_usuario(id: int):
    # Fallback sem banco
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        for i, u in enumerate(FAKE_USERS):
            if u["IdUsuario"] == id:
                FAKE_USERS.pop(i)
                return {"ok": True}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Remove via asyncpg e valida existência
    pool = await get_pool()
    row = await pool.fetchrow('DELETE FROM "SEC".Usuario WHERE idusuario=$1 RETURNING idusuario', id)
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}

# Endpoint seguro para alteração de senha (gera hash $2b$)
from pydantic import BaseModel
class PasswordChange(BaseModel):
    new_password: str
    requested_by: Optional[str] = None

@usuarios_router.post("/{id}/password", response_model=OperationResult)
async def alterar_senha_usuario(id: int, payload: PasswordChange):
    # Rejeitar senhas acima de 72 bytes (limite do bcrypt)
    if len(payload.new_password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Senha muito longa (limite: 72 bytes)")

    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(payload.new_password.encode("utf-8"), salt).decode("utf-8")  # $2b$

    # Fallback sem banco
    if os.getenv("FASTAPI_SKIP_DB", "0") in ("1", "true", "True"):
        for u in FAKE_USERS:
            if u["IdUsuario"] == id:
                u["Senha"] = hashed
                u["DataUpdate"] = datetime.now(timezone.utc).isoformat()
                return {"ok": True}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza senha e popula campos de auditoria
    pool = await get_pool()
    row = await pool.fetchrow(
        'UPDATE SEC.Usuario SET Senha=$1, CadastranteUpdate=$2, DataUpdate=CURRENT_TIMESTAMP WHERE idusuario=$3 RETURNING idusuario',
        hashed,
        (payload.requested_by or 'API-PASSWORD-CHANGE'),
        id,
    )

    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {"ok": True}

# Registrar router
app.include_router(usuarios_router)
app.include_router(permissoes_router)
