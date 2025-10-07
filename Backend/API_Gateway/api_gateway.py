"""
API Gateway Implementation
Advanced API Gateway with intelligent request routing, rate limiting, and centralized authentication
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
from ..Redis.client import get_redis_client
from ..Service_Mesh.service_mesh import service_mesh
from ..Security.security_service import ultra_security_service


class RouteStrategy(Enum):
    """Route strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    GEOGRAPHIC = "geographic"


@dataclass
class ServiceRoute:
    """Service route definition"""
    route_id: str
    path_prefix: str
    service_name: str
    target_url: str
    priority: int = 1
    rate_limit: int = 1000  # requests per minute
    auth_required: bool = True
    active: bool = True


@dataclass
class RateLimitRule:
    """Rate limit rule"""
    client_id: str
    route_id: str
    limit: int
    window_seconds: int
    current_count: int = 0
    last_reset: float = 0


class APIGateway:
    """Advanced API Gateway with intelligent routing and security"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.gateway_prefix = "api_gateway"

        # Service routes
        self.routes: Dict[str, ServiceRoute] = {}
        self.route_cache: Dict[str, str] = {}  # path -> route_id

        # Rate limiting
        self.rate_limits: Dict[str, RateLimitRule] = {}

        # Gateway statistics
        self.stats = {
            "requests_processed": 0,
            "requests_blocked": 0,
            "rate_limited": 0,
            "auth_failures": 0,
            "routing_errors": 0
        }

        # HTTP client session
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> bool:
        """Initialize API Gateway"""
        try:
            # Initialize HTTP session
            self.http_session = aiohttp.ClientSession()

            # Register default routes
            await self.register_default_routes()

            # Start background tasks
            asyncio.create_task(self.cleanup_expired_limits())

            print("✅ API Gateway initialized")
            return True

        except Exception as e:
            print(f"❌ API Gateway initialization failed: {e}")
            return False

    async def register_default_routes(self):
        """Register default service routes"""
        # FastAPI service route
        await self.register_route(ServiceRoute(
            route_id="fastapi_service",
            path_prefix="/api/fastapi",
            service_name="fastapi",
            target_url="http://fastapi:8000",
            priority=1,
            rate_limit=2000,
            auth_required=True
        ))

        # NestJS service route
        await self.register_route(ServiceRoute(
            route_id="nestjs_service",
            path_prefix="/api/nestjs",
            service_name="nestjs",
            target_url="http://nestjs:3000",
            priority=1,
            rate_limit=2000,
            auth_required=True
        ))

        # Redis service route
        await self.register_route(ServiceRoute(
            route_id="redis_service",
            path_prefix="/api/redis",
            service_name="redis",
            target_url="http://nestjs:3000/redis",
            priority=2,
            rate_limit=1000,
            auth_required=True
        ))

    async def register_route(self, route: ServiceRoute) -> bool:
        """Register service route"""
        try:
            # Store route in Redis
            await self.redis_client.setex(
                f"{self.gateway_prefix}:route:{route.route_id}",
                86400,  # 24 hours
                json.dumps(asdict(route), default=str)
            )

            # Add to local cache
            self.routes[route.route_id] = route

            # Update route cache
            self.route_cache[route.path_prefix] = route.route_id

            return True

        except Exception as e:
            print(f"Route registration error: {e}")
            return False

    async def route_request(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        client_ip: str = "unknown",
        user_agent: str = "unknown"
    ) -> Dict[str, Any]:
        """Route incoming request to appropriate service"""
        try:
            self.stats["requests_processed"] += 1

            # Find matching route
            route = await self.find_matching_route(path)
            if not route:
                self.stats["routing_errors"] += 1
                return {
                    "status": 404,
                    "error": "No matching route found",
                    "path": path
                }

            # Check rate limiting
            rate_limit_check = await self.check_rate_limit(route.route_id, client_ip)
            if not rate_limit_check["allowed"]:
                self.stats["rate_limited"] += 1
                return {
                    "status": 429,
                    "error": "Rate limit exceeded",
                    "retry_after": rate_limit_check["retry_after"]
                }

            # Check authentication if required
            if route.auth_required:
                auth_check = await self.check_authentication(headers)
                if not auth_check["authenticated"]:
                    self.stats["auth_failures"] += 1
                    return {
                        "status": 401,
                        "error": "Authentication required",
                        "reason": auth_check["reason"]
                    }

            # Route to service using service mesh
            service_instance = await service_mesh.route_request(
                route.service_name,
                routing_strategy="least_loaded"
            )

            if not service_instance:
                self.stats["routing_errors"] += 1
                return {
                    "status": 503,
                    "error": "Service unavailable",
                    "service": route.service_name
                }

            # Forward request to service
            response = await self.forward_request(
                service_instance,
                path,
                method,
                headers,
                body
            )

            return response

        except Exception as e:
            self.stats["routing_errors"] += 1
            print(f"Request routing error: {e}")
            return {
                "status": 500,
                "error": "Internal server error",
                "details": str(e)
            }

    async def find_matching_route(self, path: str) -> Optional[ServiceRoute]:
        """Find matching route for path"""
        # Check cache first
        for prefix, route_id in self.route_cache.items():
            if path.startswith(prefix):
                return self.routes.get(route_id)

        # Check all routes
        for route in self.routes.values():
            if path.startswith(route.path_prefix):
                # Update cache
                self.route_cache[route.path_prefix] = route.route_id
                return route

        return None

    async def check_rate_limit(self, route_id: str, client_id: str) -> Dict[str, Any]:
        """Check rate limit for client and route"""
        try:
            limit_key = f"{route_id}:{client_id}"
            current_time = time.time()

            # Get existing limit rule
            limit_rule = self.rate_limits.get(limit_key)

            if not limit_rule:
                # Create new limit rule based on route configuration
                route = self.routes.get(route_id)
                if not route:
                    return {"allowed": True}

                limit_rule = RateLimitRule(
                    client_id=client_id,
                    route_id=route_id,
                    limit=route.rate_limit,
                    window_seconds=60  # 1 minute window
                )
                self.rate_limits[limit_key] = limit_rule

            # Check if window has expired
            if current_time - limit_rule.last_reset > limit_rule.window_seconds:
                limit_rule.current_count = 0
                limit_rule.last_reset = current_time

            # Check if limit exceeded
            if limit_rule.current_count >= limit_rule.limit:
                retry_after = limit_rule.window_seconds - (current_time - limit_rule.last_reset)
                return {
                    "allowed": False,
                    "retry_after": max(0, int(retry_after))
                }

            # Increment counter
            limit_rule.current_count += 1

            return {"allowed": True}

        except Exception as e:
            print(f"Rate limit check error: {e}")
            # Fail open - allow request
            return {"allowed": True}

    async def check_authentication(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check authentication for request"""
        try:
            # Extract authentication header
            auth_header = headers.get("Authorization", "")
            if not auth_header:
                return {"authenticated": False, "reason": "Missing authorization header"}

            # Extract token
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                return {"authenticated": False, "reason": "Invalid authorization format"}

            # Validate session using security service
            context = {
                "ip_address": headers.get("X-Forwarded-For", "unknown"),
                "user_agent": headers.get("User-Agent", "unknown")
            }

            validation_result = await ultra_security_service.validate_session(token, context)

            if validation_result.get("valid"):
                return {
                    "authenticated": True,
                    "user_id": validation_result.get("user_id"),
                    "security_level": validation_result.get("security_level")
                }
            else:
                return {
                    "authenticated": False,
                    "reason": validation_result.get("reason", "Invalid session")
                }

        except Exception as e:
            print(f"Authentication check error: {e}")
            return {"authenticated": False, "reason": "Authentication system error"}

    async def forward_request(
        self,
        service_instance: Any,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Forward request to service instance"""
        try:
            if not self.http_session:
                self.http_session = aiohttp.ClientSession()

            # Construct target URL
            target_url = f"http://{service_instance.host}:{service_instance.port}{path}"

            # Prepare request
            request_kwargs = {
                "method": method,
                "headers": headers,
                "timeout": aiohttp.ClientTimeout(total=30)
            }

            if body and method in ["POST", "PUT", "PATCH"]:
                request_kwargs["data"] = body

            # Make request
            async with self.http_session.request(target_url, **request_kwargs) as response:
                # Read response
                response_body = await response.read()
                response_headers = dict(response.headers)

                return {
                    "status": response.status,
                    "headers": response_headers,
                    "body": response_body,
                    "service": service_instance.service_name
                }

        except Exception as e:
            print(f"Request forwarding error: {e}")
            return {
                "status": 502,
                "error": "Bad gateway",
                "details": str(e)
            }

    async def cleanup_expired_limits(self):
        """Clean up expired rate limit rules"""
        while True:
            try:
                current_time = time.time()
                expired_keys = []

                for key, rule in self.rate_limits.items():
                    if current_time - rule.last_reset > 3600:  # 1 hour
                        expired_keys.append(key)

                for key in expired_keys:
                    del self.rate_limits[key]

                await asyncio.sleep(300)  # Clean up every 5 minutes

            except Exception as e:
                print(f"Rate limit cleanup error: {e}")
                await asyncio.sleep(60)

    async def get_gateway_statistics(self) -> Dict[str, Any]:
        """Get API Gateway statistics"""
        try:
            # Get service mesh statistics
            mesh_stats = await service_mesh.get_mesh_statistics()

            return {
                "gateway_stats": self.stats.copy(),
                "active_routes": len(self.routes),
                "active_rate_limits": len(self.rate_limits),
                "service_mesh_stats": mesh_stats,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        """Close API Gateway connections"""
        if self.http_session:
            await self.http_session.close()


# Global API Gateway instance
api_gateway = APIGateway()