"""
Redis queue operations
"""
import json
from typing import Optional, Dict, Any
from .client import get_redis_client

async def enqueue_job(queue_name: str, job_data: Dict[str, Any]) -> bool:
    """Add job to queue"""
    redis_client = get_redis_client()
    try:
        job_json = json.dumps(job_data)
        await redis_client.lpush(f"queue:{queue_name}", job_json)
        return True
    except Exception as e:
        print(f"Redis enqueue error: {e}")
        return False

async def dequeue_job(queue_name: str) -> Optional[Dict[str, Any]]:
    """Get job from queue"""
    redis_client = get_redis_client()
    try:
        job_json = await redis_client.rpop(f"queue:{queue_name}")
        if job_json:
            return json.loads(job_json)
        return None
    except Exception as e:
        print(f"Redis dequeue error: {e}")
        return None

async def get_queue_length(queue_name: str) -> int:
    """Get queue length"""
    redis_client = get_redis_client()
    try:
        return await redis_client.llen(f"queue:{queue_name}")
    except Exception as e:
        print(f"Redis queue length error: {e}")
        return 0

async def peek_queue(queue_name: str, count: int = 5) -> list:
    """Peek at queue items without removing them"""
    redis_client = get_redis_client()
    try:
        items = await redis_client.lrange(f"queue:{queue_name}", 0, count - 1)
        return [json.loads(item) for item in items]
    except Exception as e:
        print(f"Redis peek queue error: {e}")
        return []

async def clear_queue(queue_name: str) -> bool:
    """Clear all items from queue"""
    redis_client = get_redis_client()
    try:
        await redis_client.delete(f"queue:{queue_name}")
        return True
    except Exception as e:
        print(f"Redis clear queue error: {e}")
        return False
