"""
Session Clustering - Multi-instance session support
Distributed session management across multiple application instances
"""
import json
import time
import uuid
from typing import Optional, Dict, Any, List
import asyncio

from .client import get_redis_client


class SessionCluster:
    """Distributed Session Management across multiple instances"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.session_prefix = "session_cluster"
        self.instance_id = str(uuid.uuid4())[:8]
        self.heartbeat_interval = 30  # seconds
        self.session_timeout = 3600  # 1 hour

        # Session statistics
        self.stats = {
            "created": 0,
            "accessed": 0,
            "destroyed": 0,
            "errors": 0
        }

    async def start_heartbeat(self):
        """Start sending heartbeat to maintain instance presence"""
        while True:
            try:
                await self.redis_client.setex(
                    f"{self.session_prefix}:instance:{self.instance_id}",
                    self.heartbeat_interval * 2,
                    json.dumps({
                        "instance_id": self.instance_id,
                        "timestamp": time.time(),
                        "status": "active",
                        "last_seen": time.time()
                    })
                )
            except Exception as e:
                self.stats["errors"] += 1
                print(f"Heartbeat error: {e}")

            await asyncio.sleep(self.heartbeat_interval)

    async def get_active_instances(self) -> List[Dict[str, Any]]:
        """Get all active instances in the cluster"""
        try:
            pattern = f"{self.session_prefix}:instance:*"
            keys = await self.redis_client.keys(pattern)

            active_instances = []
            for key in keys:
                instance_data = await self.redis_client.get(key)
                if instance_data:
                    data = json.loads(instance_data)
                    if time.time() - data.get("timestamp", 0) < self.heartbeat_interval * 2:
                        active_instances.append(data)

            return active_instances
        except Exception as e:
            print(f"Get instances error: {e}")
            return []

    async def create_session(self, user_id: str, data: Dict[str, Any]) -> Optional[str]:
        """Create session that can be accessed by any instance"""
        try:
            session_id = f"{self.session_prefix}:{user_id}:{uuid.uuid4().hex}"

            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "data": data,
                "created_at": time.time(),
                "instance_id": self.instance_id,
                "ttl": self.session_timeout,
                "last_accessed": time.time()
            }

            # Store session data
            await self.redis_client.setex(
                session_id,
                self.session_timeout,
                json.dumps(session_data, default=str)
            )

            # Store user -> session mapping for easy lookup
            await self.redis_client.setex(
                f"{self.session_prefix}:user:{user_id}",
                self.session_timeout,
                session_id
            )

            self.stats["created"] += 1
            return session_id
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Create session error: {e}")
            return None

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from any instance"""
        try:
            session_data = await self.redis_client.get(session_id)
            if session_data:
                data = json.loads(session_data)

                # Check if session is expired
                if time.time() - data.get("created_at", 0) > data.get("ttl", self.session_timeout):
                    await self._destroy_session(session_id, data.get("user_id"))
                    return None

                # Update last accessed time
                data["last_accessed"] = time.time()
                await self.redis_client.setex(
                    session_id,
                    self.session_timeout,
                    json.dumps(data, default=str)
                )

                self.stats["accessed"] += 1
                return data
            return None
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Get session error: {e}")
            return None

    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current session"""
        try:
            session_id = await self.redis_client.get(f"{self.session_prefix}:user:{user_id}")
            if session_id:
                return await self.get_session(session_id)
            return None
        except Exception as e:
            print(f"Get user session error: {e}")
            return None

    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_data = await self.redis_client.get(session_id)
            if session_data:
                current_data = json.loads(session_data)
                current_data["data"].update(data)
                current_data["updated_at"] = time.time()
                current_data["last_accessed"] = time.time()

                await self.redis_client.setex(
                    session_id,
                    self.session_timeout,
                    json.dumps(current_data, default=str)
                )
                return True
            return False
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Update session error: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            session_data = await self.redis_client.get(session_id)
            if session_data:
                data = json.loads(session_data)
                user_id = data.get("user_id")
                await self._destroy_session(session_id, user_id)
                self.stats["destroyed"] += 1
                return True
            return False
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Delete session error: {e}")
            return False

    async def _destroy_session(self, session_id: str, user_id: str = None):
        """Internal method to destroy session and mappings"""
        # Remove session
        await self.redis_client.delete(session_id)

        # Remove user mapping if provided
        if user_id:
            await self.redis_client.delete(f"{self.session_prefix}:user:{user_id}")

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            pattern = f"{self.session_prefix}:*:*"
            keys = await self.redis_client.keys(pattern)

            cleaned = 0
            for key in keys:
                session_data = await self.redis_client.get(key)
                if session_data:
                    data = json.loads(session_data)
                    if time.time() - data.get("created_at", 0) > data.get("ttl", self.session_timeout):
                        user_id = data.get("user_id")
                        await self._destroy_session(key, user_id)
                        cleaned += 1

            return cleaned
        except Exception as e:
            print(f"Cleanup error: {e}")
            return 0

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session cluster statistics"""
        try:
            # Get all sessions
            pattern = f"{self.session_prefix}:*:*"
            keys = await self.redis_client.keys(pattern)

            total_sessions = len(keys)
            active_instances = await self.get_active_instances()

            # Count sessions by instance
            instance_sessions = {}
            for key in keys[:100]:  # Sample for performance
                session_data = await self.redis_client.get(key)
                if session_data:
                    data = json.loads(session_data)
                    instance_id = data.get("instance_id", "unknown")
                    instance_sessions[instance_id] = instance_sessions.get(instance_id, 0) + 1

            return {
                "total_sessions": total_sessions,
                "active_instances": len(active_instances),
                "sessions_by_instance": instance_sessions,
                "current_instance": self.instance_id,
                "stats": self.stats
            }
        except Exception as e:
            print(f"Session stats error: {e}")
            return {"error": str(e)}


# Global session cluster instance
session_cluster = SessionCluster()
