"""
Test Redis Connection
Minimal test to verify Redis connectivity
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import redis.asyncio as redis
import os


async def test_redis():
    """Test Redis connection directly"""
    print("🚀 Testing Redis connection...")
    
    try:
        # Create Redis client directly
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            max_connections=20
        )
        
        # Test connection
        await redis_client.ping()
        print("✅ Redis connection successful")
        
        # Test basic operations
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        print(f"✅ Redis set/get working: {value}")
        
        # Clean up
        await redis_client.delete("test_key")
        
        # Close connection
        await redis_client.close()
        
        print("\n🎉 Redis test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_redis())
        if result:
            print("\n✅ Redis connection test passed!")
            sys.exit(0)
        else:
            print("\n❌ Redis connection test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)