"""
Simple Service Communication Test
Minimal test to verify Redis connectivity and basic service communication
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set environment variables for Redis connection
os.environ.setdefault('REDIS_HOST', 'localhost')
os.environ.setdefault('REDIS_PORT', '6379')
os.environ.setdefault('REDIS_PASSWORD', 'redispassword')

from Backend.Redis.client import get_redis_client, test_redis_connection
from Backend.Service_Registry.service_registry import service_registry
from Backend.Service_Mesh.service_mesh import service_mesh


async def simple_test():
    """Simple test to verify basic service communication"""
    print("🚀 Starting simple service communication test...")
    
    # Test 1: Redis connection
    print("\n1. Testing Redis connection...")
    try:
        # Test Redis connection directly
        client = get_redis_client()
        await client.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        return False
    
    # Test 2: Service registry
    print("\n2. Testing service registry...")
    try:
        # Register a test service
        service_id = await service_registry.register_service(
            service_name="test_service",
            host="localhost",
            port=8000,
            metadata={"test": True}
        )
        
        if service_id:
            print("✅ Service registered successfully")
            
            # Test service discovery
            services = await service_registry.discover_services("test_service")
            if services:
                print("✅ Service discovery working")
            else:
                print("❌ Service discovery failed")
                
            # Unregister service
            await service_registry.unregister_service(service_id)
            print("✅ Service unregistered successfully")
        else:
            print("❌ Service registration failed")
    except Exception as e:
        print(f"❌ Service registry test failed: {e}")
        return False
    
    # Test 3: Service mesh
    print("\n3. Testing service mesh...")
    try:
        # Register a test service instance
        instance_id = await service_mesh.register_service(
            service_name="test_mesh_service",
            host="localhost",
            port=8000,
            metadata={"test": True}
        )
        
        if instance_id:
            print("✅ Service mesh registration successful")
            
            # Test service routing
            instances = await service_mesh.get_service_instances("test_mesh_service")
            if instances:
                print("✅ Service mesh discovery working")
            else:
                print("❌ Service mesh discovery failed")
                
            # Unregister service
            await service_mesh.unregister_service(instance_id)
            print("✅ Service mesh unregistration successful")
        else:
            print("❌ Service mesh registration failed")
    except Exception as e:
        print(f"❌ Service mesh test failed: {e}")
        return False
    
    print("\n🎉 Simple service communication test completed successfully!")
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(simple_test())
        if result:
            print("\n✅ Simple test passed! Basic service communication is working.")
            sys.exit(0)
        else:
            print("\n❌ Simple test failed! Please check the service configurations.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)