"""
Redis Streams - Advanced messaging and event streaming
"""
from typing import List, Dict, Any, Optional
from .client import get_redis_client

async def create_stream(stream_name: str) -> bool:
    """Create a new Redis stream"""
    redis_client = get_redis_client()
    try:
        # XADD with maxlen to create stream
        await redis_client.xadd(stream_name, {"created": "true"}, maxlen=10000)
        await redis_client.xtrim(stream_name, maxlen=10000)
        return True
    except Exception as e:
        print(f"Redis create stream error: {e}")
        return False

async def add_to_stream(stream_name: str, data: Dict[str, Any]) -> str:
    """Add message to Redis stream"""
    redis_client = get_redis_client()
    try:
        message_id = await redis_client.xadd(stream_name, data)
        return message_id
    except Exception as e:
        print(f"Redis add to stream error: {e}")
        return ""

async def read_from_stream(stream_name: str, count: int = 10, block: int = 0) -> List[Dict[str, Any]]:
    """Read messages from Redis stream"""
    redis_client = get_redis_client()
    try:
        if block > 0:
            # Blocking read
            messages = await redis_client.xread({stream_name: '0-0'}, count=count, block=block)
        else:
            # Non-blocking read
            messages = await redis_client.xread({stream_name: '0-0'}, count=count)

        result = []
        if messages:
            for stream_messages in messages:
                stream, msgs = stream_messages
                for msg_id, fields in msgs:
                    result.append({
                        "id": msg_id,
                        "stream": stream,
                        "data": fields
                    })
        return result
    except Exception as e:
        print(f"Redis read from stream error: {e}")
        return []

async def get_stream_info(stream_name: str) -> Dict[str, Any]:
    """Get stream information"""
    redis_client = get_redis_client()
    try:
        info = await redis_client.xinfo_stream(stream_name)
        return {
            "length": info.get("length", 0),
            "first_entry": info.get("first-entry", {}),
            "last_entry": info.get("last-entry", {}),
            "groups": info.get("groups", [])
        }
    except Exception as e:
        print(f"Redis stream info error: {e}")
        return {}

async def create_consumer_group(stream_name: str, group_name: str) -> bool:
    """Create consumer group for stream"""
    redis_client = get_redis_client()
    try:
        await redis_client.xgroup_create(stream_name, group_name, mkstream=True)
        return True
    except Exception as e:
        print(f"Redis create consumer group error: {e}")
        return False

async def read_from_group(stream_name: str, group_name: str, consumer_name: str) -> List[Dict[str, Any]]:
    """Read messages from consumer group"""
    redis_client = get_redis_client()
    try:
        messages = await redis_client.xreadgroup(
            group_name,
            consumer_name,
            {stream_name: '>'},
            count=10
        )

        result = []
        if messages:
            for stream_messages in messages:
                stream, msgs = stream_messages
                for msg_id, fields in msgs:
                    result.append({
                        "id": msg_id,
                        "stream": stream,
                        "data": fields
                    })
        return result
    except Exception as e:
        print(f"Redis read from group error: {e}")
        return []

async def acknowledge_message(stream_name: str, group_name: str, message_id: str) -> bool:
    """Acknowledge processed message"""
    redis_client = get_redis_client()
    try:
        await redis_client.xack(stream_name, group_name, message_id)
        return True
    except Exception as e:
        print(f"Redis acknowledge error: {e}")
        return False
