"""
Service Mesh Implementation
Advanced microservices communication and management with Redis
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum

from .client import get_redis_client


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInstance:
    """Service instance information"""
    service_name: str
    instance_id: str
    host: str
    port: int
    status: ServiceStatus
    last_heartbeat: float
    metadata: Dict[str, Any]
    load_score: float = 0.0


@dataclass
class CircuitBreakerState:
    """Circuit breaker state"""
    service_name: str
    state: str  # closed, open, half_open
    failure_count: int
    last_failure_time: float
    next_retry_time: float


class ServiceMesh:
    """Advanced service mesh implementation with Redis"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.mesh_prefix = "service_mesh"

        # Service registry
        self.service_registry: Dict[str, List[ServiceInstance]] = {}
        self.heartbeat_interval = 30  # seconds

        # Circuit breaker states
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}

        # Service mesh statistics
        self.stats = {
            "services_registered": 0,
            "heartbeats_received": 0,
            "requests_routed": 0,
            "circuit_breaker_trips": 0,
            "errors": 0
        }

    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Register service instance"""
        instance_id = str(uuid.uuid4())

        instance = ServiceInstance(
            service_name=service_name,
            instance_id=instance_id,
            host=host,
            port=port,
            status=ServiceStatus.HEALTHY,
            last_heartbeat=time.time(),
            metadata=metadata or {},
            load_score=0.0
        )

        try:
            # Store instance data
            await self.redis_client.setex(
                f"{self.mesh_prefix}:instance:{instance_id}",
                86400,  # 24 hours
                json.dumps(asdict(instance), default=str)
            )

            # Add to service registry
            await self.redis_client.sadd(
                f"{self.mesh_prefix}:service:{service_name}",
                instance_id
            )

            # Update statistics
            if service_name not in [inst.service_name for instances in self.service_registry.values() for inst in instances]:
                self.stats["services_registered"] += 1

            return instance_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Service registration error: {e}")
            return ""

    async def unregister_service(self, instance_id: str) -> bool:
        """Unregister service instance"""
        try:
            # Get instance data
            instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

            if instance_data:
                instance = ServiceInstance(**json.loads(instance_data))

                # Remove from service registry
                await self.redis_client.srem(
                    f"{self.mesh_prefix}:service:{instance.service_name}",
                    instance_id
                )

                # Remove instance data
                await self.redis_client.delete(f"{self.mesh_prefix}:instance:{instance_id}")

                return True

            return False

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Service unregistration error: {e}")
            return False

    async def send_heartbeat(self, instance_id: str, load_score: float = 0.0) -> bool:
        """Send heartbeat for service instance"""
        try:
            # Get current instance data
            instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

            if instance_data:
                instance = ServiceInstance(**json.loads(instance_data))
                instance.last_heartbeat = time.time()
                instance.load_score = load_score

                # Update instance data
                await self.redis_client.setex(
                    f"{self.mesh_prefix}:instance:{instance_id}",
                    86400,
                    json.dumps(asdict(instance), default=str)
                )

                self.stats["heartbeats_received"] += 1
                return True

            return False

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Heartbeat error: {e}")
            return False

    async def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all instances of a service"""
        try:
            # Get instance IDs for service
            instance_ids = await self.redis_client.smembers(f"{self.mesh_prefix}:service:{service_name}")

            instances = []

            for instance_id in instance_ids:
                instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

                if instance_data:
                    instance = ServiceInstance(**json.loads(instance_data))

                    # Check if instance is alive (heartbeat within last 60 seconds)
                    if time.time() - instance.last_heartbeat < 60:
                        instances.append(instance)
                    else:
                        # Mark as unhealthy and remove
                        instance.status = ServiceStatus.UNHEALTHY
                        await self.unregister_service(instance_id)

            return instances

        except Exception as e:
            print(f"Service instances retrieval error: {e}")
            return []

    async def route_request(
        self,
        service_name: str,
        routing_strategy: str = "round_robin"
    ) -> Optional[ServiceInstance]:
        """Route request to service instance using specified strategy"""
        try:
            instances = await self.get_service_instances(service_name)

            if not instances:
                return None

            # Filter healthy instances
            healthy_instances = [inst for inst in instances if inst.status == ServiceStatus.HEALTHY]

            if not healthy_instances:
                return None

            # Apply routing strategy
            if routing_strategy == "round_robin":
                return await self.round_robin_routing(healthy_instances)
            elif routing_strategy == "least_loaded":
                return await self.least_loaded_routing(healthy_instances)
            elif routing_strategy == "random":
                return await self.random_routing(healthy_instances)
            else:
                return healthy_instances[0]  # Default to first

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Request routing error: {e}")
            return None

    async def round_robin_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin load balancing"""
        # Simple round-robin using Redis counter
        service_key = f"{self.mesh_prefix}:rr_counter:{instances[0].service_name}"
        counter = await self.redis_client.incr(service_key)

        return instances[counter % len(instances)]

    async def least_loaded_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Route to least loaded instance"""
        # Sort by load score (lower is better)
        sorted_instances = sorted(instances, key=lambda x: x.load_score)
        return sorted_instances[0]

    async def random_routing(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random routing"""
        import random
        return random.choice(instances)

    async def check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker is open for service"""
        circuit_breaker = self.circuit_breakers.get(service_name)

        if not circuit_breaker:
            return True  # No circuit breaker, allow request

        current_time = time.time()

        if circuit_breaker.state == "open":
            if current_time >= circuit_breaker.next_retry_time:
                # Transition to half-open
                circuit_breaker.state = "half_open"
                return True  # Allow test request
            else:
                return False  # Circuit breaker open

        return True  # Circuit breaker closed or half-open

    async def record_request_result(
        self,
        service_name: str,
        instance_id: str,
        success: bool,
        response_time_ms: float
    ) -> None:
        """Record request result for circuit breaker logic"""
        try:
            circuit_breaker = self.circuit_breakers.get(service_name)

            if not circuit_breaker:
                circuit_breaker = CircuitBreakerState(
                    service_name=service_name,
                    state="closed",
                    failure_count=0,
                    last_failure_time=0,
                    next_retry_time=0
                )
                self.circuit_breakers[service_name] = circuit_breaker

            if success:
                # Reset failure count on success
                circuit_breaker.failure_count = 0
                circuit_breaker.state = "closed"
            else:
                # Increment failure count
                circuit_breaker.failure_count += 1
                circuit_breaker.last_failure_time = time.time()

                # Check if circuit breaker should trip
                if circuit_breaker.failure_count >= 5:  # Threshold
                    circuit_breaker.state = "open"
                    circuit_breaker.next_retry_time = time.time() + 60  # Retry after 1 minute
                    self.stats["circuit_breaker_trips"] += 1

        except Exception as e:
            print(f"Circuit breaker update error: {e}")

    async def get_service_discovery_info(self) -> Dict[str, Any]:
        """Get comprehensive service discovery information"""
        try:
            # Get all services
            pattern = f"{self.mesh_prefix}:service:*"
            service_keys = await self.redis_client.keys(pattern)

            services = {}

            for service_key in service_keys:
                service_name = service_key.split(":")[-1]
                instances = await self.get_service_instances(service_name)

                services[service_name] = {
                    "instance_count": len(instances),
                    "healthy_instances": len([inst for inst in instances if inst.status == ServiceStatus.HEALTHY]),
                    "instances": [asdict(inst) for inst in instances]
                }

            return {
                "total_services": len(services),
                "services": services,
                "mesh_health": self.calculate_mesh_health(services)
            }

        except Exception as e:
            print(f"Service discovery error: {e}")
            return {"error": str(e)}

    def calculate_mesh_health(self, services: Dict[str, Any]) -> str:
        """Calculate overall service mesh health"""
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

    async def get_load_balancing_analytics(self) -> Dict[str, Any]:
        """Get load balancing analytics"""
        try:
            # Get all instances
            pattern = f"{self.mesh_prefix}:instance:*"
            instance_keys = await self.redis_client.keys(pattern)

            load_distribution = []
            service_load = {}

            for instance_key in instance_keys:
                instance_data = await self.redis_client.get(instance_key)

                if instance_data:
                    instance = ServiceInstance(**json.loads(instance_data))

                    load_distribution.append(instance.load_score)

                    if instance.service_name not in service_load:
                        service_load[instance.service_name] = []

                    service_load[instance.service_name].append(instance.load_score)

            # Calculate statistics
            if load_distribution:
                avg_load = sum(load_distribution) / len(load_distribution)
                max_load = max(load_distribution)
                min_load = min(load_distribution)

                # Load balancing efficiency
                load_variance = sum((load - avg_load) ** 2 for load in load_distribution) / len(load_distribution)
                load_std_dev = load_variance ** 0.5

                return {
                    "total_instances": len(load_distribution),
                    "load_statistics": {
                        "average": round(avg_load, 2),
                        "minimum": round(min_load, 2),
                        "maximum": round(max_load, 2),
                        "standard_deviation": round(load_std_dev, 2)
                    },
                    "load_balancing_efficiency": "excellent" if load_std_dev < 0.3 else "good" if load_std_dev < 0.6 else "needs_improvement",
                    "service_load_distribution": {
                        service: {
                            "instances": len(loads),
                            "avg_load": round(sum(loads) / len(loads), 2),
                            "max_load": round(max(loads), 2)
                        } for service, loads in service_load.items()
                    }
                }
            else:
                return {"message": "No load data available"}

        except Exception as e:
            print(f"Load balancing analytics error: {e}")
            return {"error": str(e)}

    async def implement_auto_scaling(self, service_name: str, target_load: float = 0.7) -> Dict[str, Any]:
        """Implement auto-scaling based on load"""
        try:
            instances = await self.get_service_instances(service_name)

            if not instances:
                return {"error": "No instances found for service"}

            # Calculate current average load
            total_load = sum(inst.load_score for inst in instances)
            current_avg_load = total_load / len(instances)

            scaling_decision = {
                "service_name": service_name,
                "current_instances": len(instances),
                "current_avg_load": round(current_avg_load, 2),
                "target_load": target_load,
                "action": "none",
                "reason": ""
            }

            # Scale up if average load is above target
            if current_avg_load > target_load and len(instances) < 10:  # Max 10 instances
                scaling_decision["action"] = "scale_up"
                scaling_decision["reason"] = f"Average load ({current_avg_load:.2f}) above target ({target_load})"
                scaling_decision["recommended_instances"] = min(len(instances) + 1, 10)

            # Scale down if average load is well below target
            elif current_avg_load < target_load * 0.5 and len(instances) > 1:
                scaling_decision["action"] = "scale_down"
                scaling_decision["reason"] = f"Average load ({current_avg_load:.2f}) well below target ({target_load})"
                scaling_decision["recommended_instances"] = max(len(instances) - 1, 1)

            return scaling_decision

        except Exception as e:
            print(f"Auto-scaling error: {e}")
            return {"error": str(e)}

    async def start_service_monitoring(self) -> None:
        """Start continuous service monitoring"""
        while True:
            try:
                # Check for dead instances
                await self.cleanup_dead_instances()

                # Update circuit breaker states
                await self.update_circuit_breakers()

                # Perform health checks
                await self.perform_health_checks()

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                print(f"Service monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def cleanup_dead_instances(self) -> int:
        """Clean up instances that haven't sent heartbeat"""
        try:
            pattern = f"{self.mesh_prefix}:instance:*"
            instance_keys = await self.redis_client.keys(pattern)

            cleaned = 0

            for instance_key in instance_keys:
                instance_data = await self.redis_client.get(instance_key)

                if instance_data:
                    instance = ServiceInstance(**json.loads(instance_data))

                    # Check if instance is dead (no heartbeat for 2 minutes)
                    if time.time() - instance.last_heartbeat > 120:
                        await self.unregister_service(instance.instance_id)
                        cleaned += 1

            return cleaned

        except Exception as e:
            print(f"Instance cleanup error: {e}")
            return 0

    async def update_circuit_breakers(self) -> None:
        """Update circuit breaker states"""
        current_time = time.time()

        for service_name, circuit_breaker in self.circuit_breakers.items():
            if circuit_breaker.state == "half_open":
                # Transition back to closed if enough time has passed
                if current_time - circuit_breaker.last_failure_time > 300:  # 5 minutes
                    circuit_breaker.state = "closed"
                    circuit_breaker.failure_count = 0

    async def perform_health_checks(self) -> None:
        """Perform health checks on all services"""
        try:
            pattern = f"{self.mesh_prefix}:service:*"
            service_keys = await self.redis_client.keys(pattern)

            for service_key in service_keys:
                service_name = service_key.split(":")[-1]
                instances = await self.get_service_instances(service_name)

                for instance in instances:
                    # Simple health check (in production, would make HTTP requests)
                    if time.time() - instance.last_heartbeat > 60:
                        instance.status = ServiceStatus.DEGRADED
                    else:
                        instance.status = ServiceStatus.HEALTHY

        except Exception as e:
            print(f"Health check error: {e}")

    async def get_mesh_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service mesh statistics"""
        try:
            services = await self.get_service_discovery_info()
            load_analytics = await self.get_load_balancing_analytics()

            # Get circuit breaker information
            circuit_breaker_info = {}
            for service_name, cb in self.circuit_breakers.items():
                circuit_breaker_info[service_name] = {
                    "state": cb.state,
                    "failure_count": cb.failure_count,
                    "last_failure": cb.last_failure_time,
                    "next_retry": cb.next_retry_time
                }

            return {
                "service_discovery": services,
                "load_balancing": load_analytics,
                "circuit_breakers": circuit_breaker_info,
                "mesh_health": services.get("mesh_health", "unknown"),
                "total_requests_routed": self.stats["requests_routed"],
                "circuit_breaker_trips": self.stats["circuit_breaker_trips"],
                "services_registered": self.stats["services_registered"],
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global service mesh instance
service_mesh = ServiceMesh()
