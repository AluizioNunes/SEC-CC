"""
Redis session management
"""
import json
import time
from typing import Optional, Dict, Any
from .client import get_redis_client

async def create_session(user_id: str, data: Dict[str, Any]) -> str:
    """Create user session"""
    redis_client = get_redis_client()
    session_id = f"session:{user_id}:{int(time.time())}"
    session_data = json.dumps(data)
    await redis_client.setex(session_id, 3600, session_data)  # 1 hour TTL
    return session_id

async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data"""
    redis_client = get_redis_client()
    session_data = await redis_client.get(session_id)
    if session_data:
        return json.loads(session_data)
    return None

async def delete_session(session_id: str) -> bool:
    """Delete session"""
    redis_client = get_redis_client()
    try:
        await redis_client.delete(session_id)
        return True
    except Exception as e:
        print(f"Redis session delete error: {e}")
        return False

async def update_session(session_id: str, data: Dict[str, Any]) -> bool:
    """Update session data"""
    redis_client = get_redis_client()
    try:
        session_data = json.dumps(data)
        await redis_client.setex(session_id, 3600, session_data)
        return True
    except Exception as e:
        print(f"Redis session update error: {e}")
        return False

async def get_user_sessions(user_id: str) -> list:
    """Get all sessions for a user"""
    redis_client = get_redis_client()
    try:
        pattern = f"session:{user_id}:*"
        keys = await redis_client.keys(pattern)
        sessions = []
        for key in keys:
            session_data = await redis_client.get(key)
            if session_data:
                sessions.append({
                    "session_id": key,
                    "data": json.loads(session_data)
                })
        return sessions
    except Exception as e:
        print(f"Redis get user sessions error: {e}")
        return []
