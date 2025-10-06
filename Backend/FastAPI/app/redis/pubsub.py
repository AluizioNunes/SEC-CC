"""
Redis Pub/Sub - Real-time messaging between services
"""
import asyncio
import json
from typing import Dict, List, Callable, Any
from .client import get_redis_client

class RedisPubSub:
    """Redis Pub/Sub manager"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.subscribers: Dict[str, List[Callable]] = {}
        self.pubsub = None

    async def publish(self, channel: str, message: Any) -> bool:
        """Publish message to channel"""
        try:
            message_json = json.dumps(message)
            await self.redis_client.publish(channel, message_json)
            return True
        except Exception as e:
            print(f"Redis publish error: {e}")
            return False

    async def subscribe(self, channel: str, callback: Callable[[str, Any], None]) -> bool:
        """Subscribe to channel"""
        try:
            if channel not in self.subscribers:
                self.subscribers[channel] = []
            self.subscribers[channel].append(callback)

            if not self.pubsub:
                self.pubsub = self.redis_client.pubsub()
                asyncio.create_task(self._listen())

            await self.pubsub.subscribe(channel)
            return True
        except Exception as e:
            print(f"Redis subscribe error: {e}")
            return False

    async def unsubscribe(self, channel: str, callback: Callable[[str, Any], None]) -> bool:
        """Unsubscribe from channel"""
        try:
            if channel in self.subscribers:
                self.subscribers[channel].remove(callback)
                if not self.subscribers[channel]:
                    del self.subscribers[channel]
                    if self.pubsub:
                        await self.pubsub.unsubscribe(channel)
            return True
        except Exception as e:
            print(f"Redis unsubscribe error: {e}")
            return False

    async def _listen(self):
        """Listen for messages in background"""
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel'].decode('utf-8')
                    data = json.loads(message['data'].decode('utf-8'))

                    # Call all subscribers for this channel
                    if channel in self.subscribers:
                        for callback in self.subscribers[channel]:
                            try:
                                callback(channel, data)
                            except Exception as e:
                                print(f"Subscriber callback error: {e}")
        except Exception as e:
            print(f"Redis pubsub listen error: {e}")

# Global PubSub instance
_pubsub_manager = None

def get_pubsub_manager() -> RedisPubSub:
    """Get global PubSub manager"""
    global _pubsub_manager
    if _pubsub_manager is None:
        _pubsub_manager = RedisPubSub()
    return _pubsub_manager

async def publish_message(channel: str, message: Any) -> bool:
    """Publish message to channel"""
    manager = get_pubsub_manager()
    return await manager.publish(channel, message)

async def subscribe_to_channel(channel: str, callback: Callable[[str, Any], None]) -> bool:
    """Subscribe to channel"""
    manager = get_pubsub_manager()
    return await manager.subscribe(channel, callback)

async def unsubscribe_from_channel(channel: str, callback: Callable[[str, Any], None]) -> bool:
    """Unsubscribe from channel"""
    manager = get_pubsub_manager()
    return await manager.unsubscribe(channel, callback)
