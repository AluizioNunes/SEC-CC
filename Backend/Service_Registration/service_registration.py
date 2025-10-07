"""
Service Registration Implementation
Automatic service registration with the service mesh
"""
import asyncio
import os
import time
from typing import Dict, Any, Optional

from ..Redis.client import get_redis_client
from ..Service_Mesh.service_mesh import service_mesh
from ..Service_Registry.service_registry import service_registry


class ServiceRegistration:
    """Service registration manager"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.registration_prefix = "service_registration"
        self.instance_id: Optional[str] = None
        self.service_name: Optional[str] = None
        self.is_registered = False

    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register service with both service mesh and service registry"""
        try:
            self.service_name = service_name

            # Register with service registry
            self.instance_id = await service_registry.register_service(
                service_name=service_name,
                host=host,
                port=port,
                metadata=metadata,
                tags=["auto-registered"]
            )

            if not self.instance_id:
                print(f"❌ Failed to register service {service_name} with service registry")
                return False

            # Register with service mesh
            mesh_instance_id = await service_mesh.register_service(
                service_name=service_name,
                host=host,
                port=port,
                metadata=metadata
            )

            if not mesh_instance_id:
                print(f"❌ Failed to register service {service_name} with service mesh")
                # Unregister from service registry
                await service_registry.unregister_service(self.instance_id)
                return False

            self.is_registered = True
            print(f"✅ Service {service_name} registered successfully with ID: {self.instance_id}")

            # Start heartbeat
            asyncio.create_task(self.send_heartbeats())

            return True

        except Exception as e:
            print(f"❌ Service registration error: {e}")
            return False

    async def send_heartbeats(self):
        """Send periodic heartbeats to maintain service registration"""
        while self.is_registered:
            try:
                if self.instance_id and self.service_name:
                    # Send heartbeat to service registry
                    await service_registry.send_heartbeat(self.instance_id)

                    # Send heartbeat to service mesh
                    # For service mesh, we'll send a load score (0.0 = no load)
                    await service_mesh.send_heartbeat(self.instance_id, 0.0)

                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                await asyncio.sleep(60)  # Wait longer before retrying

    async def unregister_service(self):
        """Unregister service from both service mesh and service registry"""
        try:
            if not self.is_registered or not self.instance_id:
                return True

            # Unregister from service mesh
            await service_mesh.unregister_service(self.instance_id)

            # Unregister from service registry
            await service_registry.unregister_service(self.instance_id)

            self.is_registered = False
            self.instance_id = None
            print(f"✅ Service {self.service_name} unregistered successfully")

            return True

        except Exception as e:
            print(f"❌ Service unregistration error: {e}")
            return False

    async def update_load_score(self, load_score: float):
        """Update load score for service mesh"""
        try:
            if self.instance_id:
                await service_mesh.send_heartbeat(self.instance_id, load_score)
        except Exception as e:
            print(f"❌ Load score update error: {e}")


# Global service registration instance
service_registration = ServiceRegistration()


async def register_current_service():
    """Register the current service based on environment variables"""
    try:
        # Get service information from environment variables
        service_name = os.getenv("SERVICE_NAME")
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "8000"))

        if not service_name:
            print("⚠️  SERVICE_NAME environment variable not set, skipping registration")
            return False

        # Register service
        success = await service_registration.register_service(
            service_name=service_name,
            host=host,
            port=port,
            metadata={
                "startup_time": time.time(),
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        )

        return success

    except Exception as e:
        print(f"❌ Current service registration error: {e}")
        return False


async def unregister_current_service():
    """Unregister the current service"""
    try:
        await service_registration.unregister_service()
    except Exception as e:
        print(f"❌ Current service unregistration error: {e}")