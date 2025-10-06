"""
Global Service Mesh - Multi-Region Architecture
Ultra-advanced service mesh with global load balancing and multi-region support
"""
import asyncio
import json
import time
import math
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .client import get_redis_client


class RegionStatus(Enum):
    """Region status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class GlobalRegion:
    """Global region information"""
    region_id: str
    name: str
    country_code: str
    coordinates: Tuple[float, float]  # latitude, longitude
    status: RegionStatus
    capacity: int
    current_load: float
    latency_ms: Dict[str, float]  # latency to other regions
    services: List[str]
    last_updated: float


@dataclass
class GlobalServiceInstance:
    """Global service instance information"""
    service_name: str
    instance_id: str
    region_id: str
    host: str
    port: int
    status: str
    last_heartbeat: float
    metadata: Dict[str, Any]
    load_score: float
    health_score: float


class GlobalServiceMesh:
    """Ultra-advanced global service mesh with multi-region support"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.mesh_prefix = "global_service_mesh"

        # Global service registry
        self.global_registry: Dict[str, List[GlobalServiceInstance]] = {}
        self.regions: Dict[str, GlobalRegion] = {}

        # Global load balancing
        self.heartbeat_interval = 30
        self.region_latency_cache: Dict[str, Dict[str, float]] = {}

        # Global mesh statistics
        self.stats = {
            "global_services": 0,
            "global_instances": 0,
            "cross_region_requests": 0,
            "global_heartbeats": 0,
            "region_failovers": 0,
            "errors": 0
        }

    async def register_global_service(
        self,
        service_name: str,
        region_id: str,
        host: str,
        port: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Register service instance in global mesh"""
        instance_id = f"{region_id}_{service_name}_{int(time.time())}"

        instance = GlobalServiceInstance(
            service_name=service_name,
            instance_id=instance_id,
            region_id=region_id,
            host=host,
            port=port,
            status="healthy",
            last_heartbeat=time.time(),
            metadata=metadata or {},
            load_score=0.0,
            health_score=1.0
        )

        try:
            # Store instance globally
            await self.redis_client.setex(
                f"{self.mesh_prefix}:instance:{instance_id}",
                86400,
                json.dumps(asdict(instance), default=str)
            )

            # Add to global service registry
            await self.redis_client.sadd(
                f"{self.mesh_prefix}:service:{service_name}",
                instance_id
            )

            # Add to region registry
            await self.redis_client.sadd(
                f"{self.mesh_prefix}:region:{region_id}",
                instance_id
            )

            return instance_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Global service registration error: {e}")
            return ""

    async def update_region_latency(self, from_region: str, to_region: str, latency_ms: float) -> None:
        """Update latency between regions"""
        try:
            # Store latency data
            await self.redis_client.setex(
                f"{self.mesh_prefix}:latency:{from_region}:{to_region}",
                3600,  # 1 hour
                str(latency_ms)
            )

            # Update region information
            if from_region not in self.region_latency_cache:
                self.region_latency_cache[from_region] = {}

            self.region_latency_cache[from_region][to_region] = latency_ms

        except Exception as e:
            print(f"Latency update error: {e}")

    async def get_optimal_region(
        self,
        service_name: str,
        user_region: str,
        user_coordinates: Tuple[float, float] = None
    ) -> Optional[str]:
        """Get optimal region for service based on user location and latency"""
        try:
            # Get all regions with the service
            service_instances = await self.get_global_service_instances(service_name)

            if not service_instances:
                return None

            # Group instances by region
            region_instances: Dict[str, List[GlobalServiceInstance]] = {}
            for instance in service_instances:
                if instance.region_id not in region_instances:
                    region_instances[instance.region_id] = []
                region_instances[instance.region_id].append(instance)

            # Calculate scores for each region
            region_scores = {}

            for region_id, instances in region_instances.items():
                # Base score from instance health and load
                total_health = sum(inst.health_score for inst in instances)
                total_load = sum(inst.load_score for inst in instances)
                avg_health = total_health / len(instances)
                avg_load = total_load / len(instances)

                # Geographic proximity score
                geo_score = await self.calculate_geographic_score(user_region, region_id, user_coordinates)

                # Latency score
                latency_score = await self.calculate_latency_score(user_region, region_id)

                # Combine scores (weighted average)
                combined_score = (avg_health * 0.4) + (geo_score * 0.3) + (latency_score * 0.3) - (avg_load * 0.1)

                region_scores[region_id] = combined_score

            # Return region with highest score
            if region_scores:
                best_region = max(region_scores.items(), key=lambda x: x[1])
                return best_region[0]

            return None

        except Exception as e:
            print(f"Optimal region calculation error: {e}")
            return None

    async def calculate_geographic_score(
        self,
        user_region: str,
        target_region: str,
        user_coordinates: Tuple[float, float] = None
    ) -> float:
        """Calculate geographic proximity score"""
        try:
            if user_region == target_region:
                return 1.0  # Same region

            # Get region coordinates
            target_coordinates = await self.get_region_coordinates(target_region)
            if not target_coordinates or not user_coordinates:
                return 0.5  # Neutral score

            # Calculate distance using Haversine formula
            distance = self.calculate_distance(user_coordinates, target_coordinates)

            # Convert distance to score (closer = higher score)
            # Max distance ~20000km (opposite sides of earth)
            max_distance = 20000
            geo_score = max(0, 1 - (distance / max_distance))

            return geo_score

        except Exception as e:
            print(f"Geographic score calculation error: {e}")
            return 0.5

    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        R = 6371  # Earth's radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def calculate_latency_score(self, from_region: str, to_region: str) -> float:
        """Calculate latency-based score"""
        try:
            latency_key = f"{self.mesh_prefix}:latency:{from_region}:{to_region}"
            latency_data = await self.redis_client.get(latency_key)

            if latency_data:
                latency_ms = float(latency_data)

                # Score based on latency (lower latency = higher score)
                # Perfect latency < 50ms, poor latency > 500ms
                if latency_ms < 50:
                    return 1.0
                elif latency_ms < 100:
                    return 0.9
                elif latency_ms < 200:
                    return 0.7
                elif latency_ms < 500:
                    return 0.5
                else:
                    return 0.3

            return 0.5  # Neutral score for unknown latency

        except Exception:
            return 0.5

    async def get_region_coordinates(self, region_id: str) -> Optional[Tuple[float, float]]:
        """Get region coordinates"""
        try:
            # In production, this would come from a geo database
            region_coordinates = {
                "na-east": (40.7128, -74.0060),  # New York
                "na-west": (37.7749, -122.4194), # San Francisco
                "eu-west": (51.5074, -0.1278),   # London
                "eu-central": (52.5200, 13.4050), # Berlin
                "asia-east": (35.6762, 139.6503), # Tokyo
                "asia-south": (28.6139, 77.2090), # Delhi
                "sa-east": (-23.5505, -46.6333),  # São Paulo
            }

            return region_coordinates.get(region_id)

        except Exception:
            return None

    async def get_global_service_instances(self, service_name: str) -> List[GlobalServiceInstance]:
        """Get all instances of a service across all regions"""
        try:
            # Get instance IDs for service
            instance_ids = await self.redis_client.smembers(f"{self.mesh_prefix}:service:{service_name}")

            instances = []

            for instance_id in instance_ids:
                instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

                if instance_data:
                    instance = GlobalServiceInstance(**json.loads(instance_data))

                    # Check if instance is alive
                    if time.time() - instance.last_heartbeat < 60:
                        instances.append(instance)
                    else:
                        # Mark as unhealthy
                        instance.status = "unhealthy"
                        await self.unregister_global_service(instance_id)

            return instances

        except Exception as e:
            print(f"Global service instances retrieval error: {e}")
            return []

    async def unregister_global_service(self, instance_id: str) -> bool:
        """Unregister service instance from global mesh"""
        try:
            # Get instance data
            instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

            if instance_data:
                instance = GlobalServiceInstance(**json.loads(instance_data))

                # Remove from service registry
                await self.redis_client.srem(
                    f"{self.mesh_prefix}:service:{instance.service_name}",
                    instance_id
                )

                # Remove from region registry
                await self.redis_client.srem(
                    f"{self.mesh_prefix}:region:{instance.region_id}",
                    instance_id
                )

                # Remove instance data
                await self.redis_client.delete(f"{self.mesh_prefix}:instance:{instance_id}")

                return True

            return False

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Global service unregistration error: {e}")
            return False

    async def route_global_request(
        self,
        service_name: str,
        user_region: str,
        user_coordinates: Tuple[float, float] = None,
        fallback_strategy: str = "nearest"
    ) -> Optional[GlobalServiceInstance]:
        """Route request to optimal global instance"""
        try:
            # Find optimal region
            optimal_region = await self.get_optimal_region(service_name, user_region, user_coordinates)

            if not optimal_region:
                return None

            # Get instances in optimal region
            instances = await self.get_service_instances_in_region(service_name, optimal_region)

            if not instances:
                # Fallback to nearest region if primary region unavailable
                if fallback_strategy == "nearest":
                    nearest_region = await self.find_nearest_region(optimal_region, user_coordinates)
                    if nearest_region:
                        instances = await self.get_service_instances_in_region(service_name, nearest_region)

            if not instances:
                return None

            # Select best instance in region
            return await self.select_best_instance_in_region(instances)

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Global request routing error: {e}")
            return None

    async def get_service_instances_in_region(self, service_name: str, region_id: str) -> List[GlobalServiceInstance]:
        """Get service instances in specific region"""
        try:
            # Get instance IDs for region
            instance_ids = await self.redis_client.smembers(f"{self.mesh_prefix}:region:{region_id}")

            instances = []

            for instance_id in instance_ids:
                instance_data = await self.redis_client.get(f"{self.mesh_prefix}:instance:{instance_id}")

                if instance_data:
                    instance = GlobalServiceInstance(**json.loads(instance_data))
                    instances.append(instance)

            return instances

        except Exception as e:
            print(f"Region instances retrieval error: {e}")
            return []

    async def find_nearest_region(
        self,
        target_region: str,
        user_coordinates: Tuple[float, float]
    ) -> Optional[str]:
        """Find nearest region to user"""
        try:
            # Get all regions
            pattern = f"{self.mesh_prefix}:region_info:*"
            region_keys = await self.redis_client.keys(pattern)

            nearest_region = None
            min_distance = float('inf')

            for region_key in region_keys:
                region_id = region_key.split(":")[-1]
                region_coordinates = await self.get_region_coordinates(region_id)

                if region_coordinates and user_coordinates:
                    distance = self.calculate_distance(user_coordinates, region_coordinates)

                    if distance < min_distance:
                        min_distance = distance
                        nearest_region = region_id

            return nearest_region

        except Exception as e:
            print(f"Nearest region calculation error: {e}")
            return None

    async def select_best_instance_in_region(self, instances: List[GlobalServiceInstance]) -> GlobalServiceInstance:
        """Select best instance in region using load balancing"""
        try:
            if not instances:
                return None

            # Filter healthy instances
            healthy_instances = [inst for inst in instances if inst.status == "healthy"]

            if not healthy_instances:
                return None

            # Use round-robin for load distribution
            region_key = f"{self.mesh_prefix}:rr_region:{instances[0].region_id}"
            counter = await self.redis_client.incr(region_key)

            return healthy_instances[counter % len(healthy_instances)]

        except Exception as e:
            print(f"Instance selection error: {e}")
            return None

    async def monitor_global_health(self) -> Dict[str, Any]:
        """Monitor global service mesh health"""
        try:
            # Get all regions
            pattern = f"{self.mesh_prefix}:region_info:*"
            region_keys = await self.redis_client.keys(pattern)

            global_health = {
                "total_regions": len(region_keys),
                "healthy_regions": 0,
                "degraded_regions": 0,
                "unhealthy_regions": 0,
                "regions": {}
            }

            for region_key in region_keys:
                region_id = region_key.split(":")[-1]
                region_info = await self.get_region_health(region_id)

                global_health["regions"][region_id] = region_info

                if region_info["status"] == "healthy":
                    global_health["healthy_regions"] += 1
                elif region_info["status"] == "degraded":
                    global_health["degraded_regions"] += 1
                else:
                    global_health["unhealthy_regions"] += 1

            # Calculate overall health score
            total_regions = global_health["total_regions"]
            if total_regions > 0:
                health_score = (global_health["healthy_regions"] * 1.0 +
                              global_health["degraded_regions"] * 0.5) / total_regions
                global_health["overall_health_score"] = round(health_score, 2)

            return global_health

        except Exception as e:
            print(f"Global health monitoring error: {e}")
            return {"error": str(e)}

    async def get_region_health(self, region_id: str) -> Dict[str, Any]:
        """Get health information for specific region"""
        try:
            instances = await self.get_service_instances_in_region("*", region_id)  # All services

            total_instances = len(instances)
            healthy_instances = len([inst for inst in instances if inst.status == "healthy"])

            # Calculate region load
            total_load = sum(inst.load_score for inst in instances)

            health_status = "healthy"
            if total_instances > 0:
                health_percentage = (healthy_instances / total_instances) * 100

                if health_percentage < 50:
                    health_status = "unhealthy"
                elif health_percentage < 80:
                    health_status = "degraded"

            return {
                "region_id": region_id,
                "status": health_status,
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "health_percentage": (healthy_instances / max(1, total_instances)) * 100,
                "total_load": total_load,
                "avg_load": total_load / max(1, total_instances),
                "last_updated": time.time()
            }

        except Exception as e:
            print(f"Region health error: {e}")
            return {"error": str(e)}

    async def start_global_monitoring(self) -> None:
        """Start global service mesh monitoring"""
        while True:
            try:
                # Update region latencies
                await self.update_region_latencies()

                # Monitor region health
                await self.monitor_region_health()

                # Cleanup dead instances
                await self.cleanup_dead_instances()

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                print(f"Global monitoring error: {e}")
                await asyncio.sleep(60)

    async def update_region_latencies(self) -> None:
        """Update latency information between regions"""
        try:
            regions = ["na-east", "na-west", "eu-west", "eu-central", "asia-east", "asia-south", "sa-east"]

            for from_region in regions:
                for to_region in regions:
                    if from_region != to_region:
                        # Calculate simulated latency (in production, would measure actual latency)
                        base_latency = self.calculate_region_distance_latency(from_region, to_region)
                        random_factor = 0.8 + (0.4 * (time.time() % 10) / 10)  # ±20% variation

                        latency_ms = base_latency * random_factor

                        await self.update_region_latency(from_region, to_region, latency_ms)

        except Exception as e:
            print(f"Region latency update error: {e}")

    def calculate_region_distance_latency(self, region1: str, region2: str) -> float:
        """Calculate base latency between regions based on geographic distance"""
        try:
            coord1 = self.get_region_coordinates(region1) or (0, 0)
            coord2 = self.get_region_coordinates(region2) or (0, 0)

            distance_km = self.calculate_distance(coord1, coord2)

            # Base latency calculation (simplified)
            # Fiber optic speed ~200,000 km/s, but add network overhead
            base_latency_ms = (distance_km / 200000) * 1000 + 10  # 10ms base overhead

            return base_latency_ms

        except Exception:
            return 100  # Default 100ms

    async def monitor_region_health(self) -> None:
        """Monitor health of all regions"""
        try:
            pattern = f"{self.mesh_prefix}:region_info:*"
            region_keys = await self.redis_client.keys(pattern)

            for region_key in region_keys:
                region_id = region_key.split(":")[-1]
                region_health = await self.get_region_health(region_id)

                # Store region health information
                await self.redis_client.setex(
                    f"{self.mesh_prefix}:region_health:{region_id}",
                    300,  # 5 minutes
                    json.dumps(region_health, default=str)
                )

        except Exception as e:
            print(f"Region health monitoring error: {e}")

    async def cleanup_dead_instances(self) -> int:
        """Clean up instances that haven't sent heartbeat"""
        try:
            pattern = f"{self.mesh_prefix}:instance:*"
            instance_keys = await self.redis_client.keys(pattern)

            cleaned = 0

            for instance_key in instance_keys:
                instance_data = await self.redis_client.get(instance_key)

                if instance_data:
                    instance = GlobalServiceInstance(**json.loads(instance_data))

                    # Check if instance is dead (no heartbeat for 2 minutes)
                    if time.time() - instance.last_heartbeat > 120:
                        await self.unregister_global_service(instance.instance_id)
                        cleaned += 1

            return cleaned

        except Exception as e:
            print(f"Global instance cleanup error: {e}")
            return 0

    async def get_global_mesh_analytics(self) -> Dict[str, Any]:
        """Get comprehensive global service mesh analytics"""
        try:
            # Get global health
            global_health = await self.monitor_global_health()

            # Get cross-region traffic
            cross_region_requests = await self.get_cross_region_traffic()

            # Get region performance
            region_performance = await self.get_region_performance_analytics()

            return {
                "global_health": global_health,
                "cross_region_traffic": cross_region_requests,
                "region_performance": region_performance,
                "global_statistics": self.stats,
                "recommendations": await self.get_global_optimization_recommendations(),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_cross_region_traffic(self) -> Dict[str, Any]:
        """Get cross-region traffic analytics"""
        try:
            # Get traffic data from Redis
            pattern = f"{self.mesh_prefix}:traffic:*"
            traffic_keys = await self.redis_client.keys(pattern)

            traffic_data = {}

            for key in traffic_keys:
                traffic = await self.redis_client.get(key)
                if traffic:
                    traffic_data[key] = json.loads(traffic)

            return {
                "total_cross_region_routes": len(traffic_data),
                "traffic_patterns": traffic_data,
                "optimization_opportunities": await self.identify_traffic_optimization_opportunities(traffic_data)
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_region_performance_analytics(self) -> Dict[str, Any]:
        """Get region performance analytics"""
        try:
            pattern = f"{self.mesh_prefix}:region_health:*"
            region_keys = await self.redis_client.keys(pattern)

            region_performance = {}

            for key in region_keys:
                region_id = key.split(":")[-1]
                performance_data = await self.redis_client.get(key)

                if performance_data:
                    region_performance[region_id] = json.loads(performance_data)

            return {
                "regions_analyzed": len(region_performance),
                "performance_by_region": region_performance,
                "global_performance_score": await self.calculate_global_performance_score(region_performance)
            }

        except Exception as e:
            return {"error": str(e)}

    async def calculate_global_performance_score(self, region_performance: Dict[str, Any]) -> float:
        """Calculate global performance score"""
        try:
            if not region_performance:
                return 0.0

            total_score = 0.0
            total_regions = 0

            for region_data in region_performance.values():
                health_percentage = region_data.get("health_percentage", 0)
                total_score += health_percentage
                total_regions += 1

            return total_score / max(1, total_regions)

        except Exception:
            return 0.0

    async def identify_traffic_optimization_opportunities(self, traffic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for traffic optimization"""
        opportunities = []

        try:
            for traffic_key, traffic_info in traffic_data.items():
                # Look for high-latency routes
                if traffic_info.get("avg_latency_ms", 0) > 200:
                    opportunities.append({
                        "type": "high_latency_route",
                        "route": traffic_key,
                        "current_latency": traffic_info["avg_latency_ms"],
                        "suggestion": "Consider CDN or edge caching",
                        "priority": "high"
                    })

                # Look for unbalanced traffic
                if traffic_info.get("request_count", 0) > 1000:
                    opportunities.append({
                        "type": "high_traffic_route",
                        "route": traffic_key,
                        "request_count": traffic_info["request_count"],
                        "suggestion": "Consider load balancing optimization",
                        "priority": "medium"
                    })

        except Exception as e:
            print(f"Traffic optimization analysis error: {e}")

        return opportunities

    async def get_global_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get global optimization recommendations"""
        recommendations = []

        try:
            # Get global health
            global_health = await self.monitor_global_health()

            # Analyze regions
            for region_id, region_info in global_health.get("regions", {}).items():
                if region_info.get("status") == "unhealthy":
                    recommendations.append({
                        "type": "region_health",
                        "region": region_id,
                        "issue": "Unhealthy region detected",
                        "recommendation": "Investigate region-specific issues",
                        "priority": "critical"
                    })

                if region_info.get("avg_load", 0) > 0.8:
                    recommendations.append({
                        "type": "high_region_load",
                        "region": region_id,
                        "issue": "High load in region",
                        "recommendation": "Consider scaling region capacity",
                        "priority": "high"
                    })

            # Analyze cross-region traffic
            traffic_data = await self.get_cross_region_traffic()

            if traffic_data.get("total_cross_region_routes", 0) > 10:
                recommendations.append({
                    "type": "traffic_optimization",
                    "issue": "High cross-region traffic",
                    "recommendation": "Consider multi-region deployment",
                    "priority": "medium"
                })

        except Exception as e:
            print(f"Optimization recommendations error: {e}")

        return recommendations


# Global service mesh instance
global_service_mesh = GlobalServiceMesh()
