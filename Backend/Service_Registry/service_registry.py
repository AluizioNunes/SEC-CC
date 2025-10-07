"""
Service Registry Implementation
Dynamic service discovery with health checking and load balancing
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ..Redis.client import get_redis_client


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    last_heartbeat: float
    metadata: Dict[str, Any]
    tags: List[str]
    version: str = "1.0.0"


class ServiceRegistry:
    """Advanced service registry with dynamic discovery"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.registry_prefix = "service_registry"

        # Service registry
        self.registered_services: Dict[str, ServiceRegistration] = {}

        # Registry statistics
        self.stats = {
            "services_registered": 0,
            "heartbeats_received": 0,
            "discovery_requests": 0,
            "health_checks": 0,
            "errors": 0
        }

    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        version: str = "1.0.0"
    ) -> str:
        """Register service instance"""
        try:
            service_id = str(uuid.uuid4())

            registration = ServiceRegistration(
                service_id=service_id,
                service_name=service_name,
                host=host,
                port=port,
                status=ServiceStatus.HEALTHY,
                last_heartbeat=time.time(),
                metadata=metadata or {},
                tags=tags or [],
                version=version
            )

            # Store in Redis
            await self.redis_client.setex(
                f"{self.registry_prefix}:service:{service_id}",
                86400,  # 24 hours
                json.dumps(asdict(registration), default=str)
            )

            # Add to service set
            await self.redis_client.sadd(
                f"{self.registry_prefix}:services:{service_name}",
                service_id
            )

            # Update local cache
            self.registered_services[service_id] = registration
            self.stats["services_registered"] += 1

            return service_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Service registration error: {e}")
            return ""

    async def unregister_service(self, service_id: str) -> bool:
        """Unregister service instance"""
        try:
            registration = self.registered_services.get(service_id)
            if not registration:
                return False

            # Remove from Redis
            await self.redis_client.srem(
                f"{self.registry_prefix}:services:{registration.service_name}",
                service_id
            )

            await self.redis_client.delete(f"{self.registry_prefix}:service:{service_id}")

            # Remove from local cache
            del self.registered_services[service_id]

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Service unregistration error: {e}")
            return False

    async def send_heartbeat(self, service_id: str) -> bool:
        """Send heartbeat for service instance"""
        try:
            registration = self.registered_services.get(service_id)
            if not registration:
                return False

            # Update heartbeat timestamp
            registration.last_heartbeat = time.time()

            # Update in Redis
            await self.redis_client.setex(
                f"{self.registry_prefix}:service:{service_id}",
                86400,
                json.dumps(asdict(registration), default=str)
            )

            self.stats["heartbeats_received"] += 1
            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Heartbeat error: {e}")
            return False

    async def discover_services(self, service_name: str) -> List[ServiceRegistration]:
        """Discover service instances by name"""
        try:
            self.stats["discovery_requests"] += 1

            # Get service IDs from Redis
            service_ids = await self.redis_client.smembers(f"{self.registry_prefix}:services:{service_name}")

            services = []

            for service_id in service_ids:
                # Try local cache first
                if service_id in self.registered_services:
                    registration = self.registered_services[service_id]
                    # Check if service is still alive
                    if time.time() - registration.last_heartbeat < 120:  # 2 minutes
                        services.append(registration)
                    else:
                        # Remove stale service
                        await self.unregister_service(service_id)
                    continue

                # Get from Redis
                service_data = await self.redis_client.get(f"{self.registry_prefix}:service:{service_id}")
                if service_data:
                    registration = ServiceRegistration(**json.loads(service_data))
                    # Check if service is still alive
                    if time.time() - registration.last_heartbeat < 120:  # 2 minutes
                        services.append(registration)
                        # Update local cache
                        self.registered_services[service_id] = registration
                    else:
                        # Remove stale service
                        await self.unregister_service(service_id)

            return services

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Service discovery error: {e}")
            return []

    async def get_service_by_id(self, service_id: str) -> Optional[ServiceRegistration]:
        """Get service by ID"""
        try:
            # Try local cache first
            if service_id in self.registered_services:
                return self.registered_services[service_id]

            # Get from Redis
            service_data = await self.redis_client.get(f"{self.registry_prefix}:service:{service_id}")
            if service_data:
                registration = ServiceRegistration(**json.loads(service_data))
                # Update local cache
                self.registered_services[service_id] = registration
                return registration

            return None

        except Exception as e:
            print(f"Get service by ID error: {e}")
            return None

    async def perform_health_check(self, service_id: str) -> ServiceStatus:
        """Perform health check on service"""
        try:
            self.stats["health_checks"] += 1

            registration = await self.get_service_by_id(service_id)
            if not registration:
                return ServiceStatus.UNKNOWN

            # Simple health check (in production, would make HTTP requests)
            if time.time() - registration.last_heartbeat > 60:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.HEALTHY

            # Update status
            registration.status = status

            # Update in Redis
            await self.redis_client.setex(
                f"{self.registry_prefix}:service:{service_id}",
                86400,
                json.dumps(asdict(registration), default=str)
            )

            # Update local cache
            if service_id in self.registered_services:
                self.registered_services[service_id] = registration

            return status

        except Exception as e:
            print(f"Health check error: {e}")
            return ServiceStatus.UNKNOWN

    async def get_service_discovery_info(self) -> Dict[str, Any]:
        """Get comprehensive service discovery information"""
        try:
            # Get all service names
            pattern = f"{self.registry_prefix}:services:*"
            service_keys = await self.redis_client.keys(pattern)

            services = {}

            for service_key in service_keys:
                service_name = service_key.split(":")[-1]
                instances = await self.discover_services(service_name)

                services[service_name] = {
                    "instance_count": len(instances),
                    "healthy_instances": len([inst for inst in instances if inst.status == ServiceStatus.HEALTHY]),
                    "instances": [asdict(inst) for inst in instances]
                }

            return {
                "total_services": len(services),
                "services": services,
                "registry_health": self.calculate_registry_health(services)
            }

        except Exception as e:
            print(f"Service discovery info error: {e}")
            return {"error": str(e)}

    def calculate_registry_health(self, services: Dict[str, Any]) -> str:
        """Calculate overall registry health"""
        if not services:
            return "unknown"

        total_instances = sum(service["instance_count"] for service in services.values())
        healthy_instances = sum(service["healthy_instances"] for service in services.values())

        if total_instances == 0:
            return "unknown"

        health_percentage = (healthy_instances / total_instances) * 100

        if health_percentage >= 90:
            return "excellent"
        elif health_percentage >= 75:
            return "good"
        elif health_percentage >= 50:
            return "fair"
        else:
            return "poor"

    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        while True:
            try:
                # Perform health checks on all services
                for service_id in list(self.registered_services.keys()):
                    await self.perform_health_check(service_id)

                # Clean up dead services
                await self.cleanup_dead_services()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(60)

    async def cleanup_dead_services(self):
        """Clean up services that haven't sent heartbeat"""
        try:
            current_time = time.time()

            for service_id, registration in list(self.registered_services.items()):
                # Check if service is dead (no heartbeat for 2 minutes)
                if current_time - registration.last_heartbeat > 120:
                    await self.unregister_service(service_id)

        except Exception as e:
            print(f"Dead service cleanup error: {e}")

    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            discovery_info = await self.get_service_discovery_info()

            return {
                "registry_stats": self.stats.copy(),
                "service_discovery": discovery_info,
                "active_services": len(self.registered_services),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global service registry instance
service_registry = ServiceRegistry()