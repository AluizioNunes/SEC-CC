"""
Redis Middleware - Global Integration
Middleware for automatic Redis feature integration
"""
import time
from typing import Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .rate_limiter import rate_limiter
from .session_cluster import session_cluster


async def global_rate_limiting_middleware(request: Request, call_next: Callable):
    """Global rate limiting middleware"""

    # Skip rate limiting for certain paths
    skip_paths = ["/health", "/metrics", "/docs", "/redoc", "/redis-advanced/health"]
    if any(path in request.url.path for path in skip_paths):
        return await call_next(request)

    # Extract client identifier (IP + User-Agent)
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    identifier = f"{client_ip}:{hash(user_agent) % 1000}"  # Simple distribution

    # Check multiple rate limits
    allowed, info = await rate_limiter.check_multiple_limits(identifier, {
        "requests_per_minute": 100,
        "requests_per_hour": 1000
    })

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "details": info,
                "retry_after": min([r.get("reset_in", 60) for r in info["results"].values() if "reset_in" in r])
            },
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(min([r.get("reset_in", 60) for r in info["results"].values() if "reset_in" in r]))
            }
        )

    # Add rate limit headers to response
    response = await call_next(request)

    if hasattr(response, 'headers'):
        # Add headers for each limit type
        for limit_type, limit_info in info["results"].items():
            response.headers[f"X-RateLimit-{limit_type.replace('_', '-').title()}"] = str(limit_info.get("current", 0))

    return response


async def session_middleware(request: Request, call_next: Callable):
    """Session management middleware"""

    # Extract session ID from cookie or header
    session_id = request.cookies.get("session_id") or request.headers.get("X-Session-ID")

    if session_id:
        # Get session data
        session_data = await session_cluster.get_session(session_id)
        if session_data:
            # Add session info to request state
            request.state.session = session_data
            request.state.user_id = session_data.get("user_id")

    response = await call_next(request)
    return response


async def request_logging_middleware(request: Request, call_next: Callable):
    """Request logging and metrics middleware"""

    start_time = time.time()

    # Generate request ID for tracing
    request_id = f"req_{int(time.time() * 1000)}_{hash(request.url.path) % 1000}"

    # Add request ID to headers for tracing
    response = await call_next(request)

    processing_time = time.time() - start_time

    # Add custom headers to response
    if hasattr(response, 'headers'):
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Processing-Time"] = f"{processing_time".3f"}s"

    return response
