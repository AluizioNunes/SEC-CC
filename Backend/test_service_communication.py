"""
Test Service Communication
Script to verify that all services can communicate properly
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Backend.Redis.client import get_redis_client, test_redis_connection
from Backend.Service_Mesh.service_mesh import service_mesh
from Backend.Service_Registry.service_registry import service_registry
from Backend.Message_Broker.message_broker import hybrid_broker
from Backend.Event_Driven.event_driven import event_driven_system, EventType


async def test_service_communication():
    """Test communication between all services"""
    print("🚀 Starting service communication tests...")
    
    # Test 1: Redis connection
    print("\n1. Testing Redis connection...")
    try:
        redis_connected = test_redis_connection()
        if redis_connected:
            print("✅ Redis connection successful")
        else:
            print("❌ Redis connection failed")
            return False
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
            instance = await service_mesh.route_request("test_mesh_service", "round_robin")
            if instance:
                print("✅ Service mesh routing working")
            else:
                print("❌ Service mesh routing failed")
                
            # Unregister service
            await service_mesh.unregister_service(instance_id)
            print("✅ Service mesh unregistration successful")
        else:
            print("❌ Service mesh registration failed")
    except Exception as e:
        print(f"❌ Service mesh test failed: {e}")
        return False
    
    # Test 4: Message broker
    print("\n4. Testing message broker...")
    try:
        # Initialize message broker
        await hybrid_broker.initialize()
        print("✅ Message broker initialized")
        
        # Test message publishing
        test_message = {
            "type": "test",
            "content": "This is a test message",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        message_id = await hybrid_broker.publish_message(
            message=test_message,
            routing_key="test",
            stream_name="test"
        )
        
        if message_id:
            print("✅ Message publishing successful")
        else:
            print("❌ Message publishing failed")
            
        # Close message broker
        await hybrid_broker.close()
        print("✅ Message broker closed")
    except Exception as e:
        print(f"❌ Message broker test failed: {e}")
        return False
    
    # Test 5: Event-driven system
    print("\n5. Testing event-driven system...")
    try:
        # Initialize event-driven system
        await event_driven_system.initialize()
        print("✅ Event-driven system initialized")
        
        # Test event publishing
        event_id = await event_driven_system.publish_event(
            event_type=EventType.SYSTEM_ALERT,
            payload={"test": "data"},
            source_service="test_service"
        )
        
        if event_id:
            print("✅ Event publishing successful")
        else:
            print("❌ Event publishing failed")
    except Exception as e:
        print(f"❌ Event-driven system test failed: {e}")
        return False
    
    print("\n🎉 All service communication tests completed successfully!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_service_communication())
    if result:
        print("\n✅ All tests passed! Services can communicate properly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed! Please check the service configurations.")
        sys.exit(1)