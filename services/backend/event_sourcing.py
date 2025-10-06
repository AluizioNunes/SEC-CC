"""
Redis Streams - Advanced Event Sourcing
Complete event sourcing implementation with Redis Streams
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum

from .client import get_redis_client


class EventType(Enum):
    """Event types for event sourcing"""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    PAYMENT_PROCESSED = "payment_processed"
    INVENTORY_UPDATED = "inventory_updated"
    SYSTEM_ALERT = "system_alert"
    DATA_EXPORTED = "data_exported"
    CACHE_INVALIDATED = "cache_invalidated"


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: str
    timestamp: float
    user_id: Optional[str]
    entity_id: Optional[str]
    entity_type: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "data": self.data,
            "metadata": self.metadata,
            "version": self.version
        }


class EventSourcingManager:
    """Advanced Event Sourcing with Redis Streams"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.events_prefix = "events"
        self.snapshots_prefix = "snapshots"

        # Event sourcing statistics
        self.stats = {
            "events_published": 0,
            "events_consumed": 0,
            "snapshots_created": 0,
            "events_replayed": 0,
            "errors": 0
        }

    async def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        user_id: str = None,
        entity_id: str = None,
        entity_type: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Publish event to Redis Streams"""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type.value,
            timestamp=time.time(),
            user_id=user_id,
            entity_id=entity_id,
            entity_type=entity_type,
            data=data,
            metadata=metadata or {}
        )

        try:
            # Publish to main events stream
            main_stream = f"{self.events_prefix}:main"
            message_id = await self.redis_client.xadd(
                main_stream,
                event.to_dict()
            )

            # Publish to entity-specific stream if entity_id provided
            if entity_id and entity_type:
                entity_stream = f"{self.events_prefix}:entity:{entity_type}:{entity_id}"
                await self.redis_client.xadd(
                    entity_stream,
                    event.to_dict()
                )

            # Publish to user-specific stream if user_id provided
            if user_id:
                user_stream = f"{self.events_prefix}:user:{user_id}"
                await self.redis_client.xadd(
                    user_stream,
                    event.to_dict()
                )

            self.stats["events_published"] += 1
            return message_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Event publish error: {e}")
            raise

    async def consume_events(
        self,
        callback: Callable[[Event], None],
        group_name: str = "event_processors",
        consumer_name: str = None,
        event_types: List[EventType] = None,
        entity_type: str = None,
        entity_id: str = None
    ) -> None:
        """
        Consume events from Redis Streams with filtering
        """
        if not consumer_name:
            consumer_name = f"consumer_{int(time.time())}"

        # Determine stream to consume from
        if entity_id and entity_type:
            stream_key = f"{self.events_prefix}:entity:{entity_type}:{entity_id}"
        else:
            stream_key = f"{self.events_prefix}:main"

        try:
            # Create consumer group if it doesn't exist
            try:
                await self.redis_client.xgroup_create(stream_key, group_name, "0", mkstream=True)
            except Exception:
                # Group already exists
                pass

            while True:
                try:
                    # Read messages from stream
                    messages = await self.redis_client.xreadgroup(
                        group_name,
                        consumer_name,
                        {stream_key: ">"},
                        count=10,
                        block=5000  # 5 seconds timeout
                    )

                    for stream_messages in messages:
                        stream, msgs = stream_messages
                        for message_id, message_data in msgs:
                            try:
                                # Filter by event type if specified
                                if event_types:
                                    event_type = message_data.get("event_type")
                                    if not any(EventType(et) == EventType(event_type) for et in event_types):
                                        await self.redis_client.xack(stream_key, group_name, message_id)
                                        continue

                                # Convert to Event object
                                event = Event(**message_data)

                                # Process event
                                await callback(event)

                                # Acknowledge message
                                await self.redis_client.xack(stream_key, group_name, message_id)

                                self.stats["events_consumed"] += 1

                            except Exception as e:
                                print(f"Event processing error: {e}")

                except asyncio.TimeoutError:
                    continue  # No messages, continue waiting
                except Exception as e:
                    print(f"Event consumption error: {e}")
                    await asyncio.sleep(5)  # Wait before retrying

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Event consumer setup error: {e}")

    async def create_snapshot(
        self,
        entity_type: str,
        entity_id: str,
        state: Dict[str, Any],
        version: int = 1
    ) -> str:
        """Create snapshot for entity state"""
        snapshot_id = str(uuid.uuid4())
        timestamp = time.time()

        snapshot_data = {
            "snapshot_id": snapshot_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "state": state,
            "version": version,
            "timestamp": timestamp,
            "created_from_events": True
        }

        try:
            snapshot_key = f"{self.snapshots_prefix}:{entity_type}:{entity_id}"
            await self.redis_client.set(
                snapshot_key,
                json.dumps(snapshot_data, default=str)
            )

            self.stats["snapshots_created"] += 1
            return snapshot_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Snapshot creation error: {e}")
            raise

    async def get_snapshot(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get latest snapshot for entity"""
        try:
            snapshot_key = f"{self.snapshots_prefix}:{entity_type}:{entity_id}"
            snapshot_data = await self.redis_client.get(snapshot_key)

            if snapshot_data:
                return json.loads(snapshot_data)
            return None

        except Exception as e:
            print(f"Snapshot retrieval error: {e}")
            return None

    async def replay_events(
        self,
        entity_type: str,
        entity_id: str,
        start_time: float = 0,
        end_time: float = None
    ) -> List[Event]:
        """Replay events for entity to rebuild state"""
        try:
            entity_stream = f"{self.events_prefix}:entity:{entity_type}:{entity_id}"

            # Get events from stream
            if end_time is None:
                end_time = time.time()

            events_data = await self.redis_client.xrange(
                entity_stream,
                min=f"{start_time}",
                max=f"{end_time}"
            )

            events = []
            for event_id, event_data in events_data:
                event = Event(**event_data)
                events.append(event)

            self.stats["events_replayed"] += len(events)
            return events

        except Exception as e:
            print(f"Event replay error: {e}")
            return []

    async def get_event_stats(self) -> Dict[str, Any]:
        """Get event sourcing statistics"""
        try:
            # Get stream information
            pattern = f"{self.events_prefix}:*"
            streams = await self.redis_client.keys(pattern)

            stream_info = {}
            for stream in streams:
                length = await self.redis_client.xlen(stream)
                groups = await self._get_stream_groups(stream)
                stream_info[stream] = {
                    "length": length,
                    "groups": groups
                }

            return {
                "events_published": self.stats["events_published"],
                "events_consumed": self.stats["events_consumed"],
                "snapshots_created": self.stats["snapshots_created"],
                "events_replayed": self.stats["events_replayed"],
                "errors": self.stats["errors"],
                "streams": stream_info,
                "event_rate": f"{round(self.stats['events_published'] / max(1, time.time() - asyncio.get_event_loop().time()), 1)}/sec"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_stream_groups(self, stream: str) -> Dict[str, Any]:
        """Get consumer groups for a stream"""
        try:
            groups = await self.redis_client.xinfo_groups(stream)
            return {group["name"]: group for group in groups}
        except Exception:
            return {}

    async def create_projection(
        self,
        projection_name: str,
        event_types: List[EventType],
        projection_function: Callable[[Event], Dict[str, Any]]
    ) -> None:
        """Create read projection from events"""
        projection_key = f"projections:{projection_name}"

        # Get all relevant events
        main_stream = f"{self.events_prefix}:main"
        events_data = await self.redis_client.xrange(main_stream, min="-", max="+")

        projection_data = {}
        for event_id, event_data in events_data:
            event = Event(**event_data)

            # Filter by event types
            if EventType(event.event_type) in event_types:
                # Apply projection function
                projection_update = await projection_function(event)
                projection_data.update(projection_update)

        # Store projection
        await self.redis_client.set(
            projection_key,
            json.dumps(projection_data, default=str)
        )

    async def get_projection(self, projection_name: str) -> Optional[Dict[str, Any]]:
        """Get read projection"""
        try:
            projection_key = f"projections:{projection_name}"
            projection_data = await self.redis_client.get(projection_key)

            if projection_data:
                return json.loads(projection_data)
            return None

        except Exception as e:
            print(f"Projection retrieval error: {e}")
            return None


# Global event sourcing manager
event_sourcing_manager = EventSourcingManager()


# Example event handlers for common business logic
async def handle_user_events(event: Event):
    """Handle user-related events"""
    if event.event_type == EventType.USER_CREATED.value:
        # Create user profile cache
        await redis_client.setex(
            f"user_profile:{event.entity_id}",
            3600,
            json.dumps(event.data, default=str)
        )

    elif event.event_type == EventType.USER_UPDATED.value:
        # Update user profile cache
        await redis_client.setex(
            f"user_profile:{event.entity_id}",
            3600,
            json.dumps(event.data, default=str)
        )

    elif event.event_type == EventType.USER_DELETED.value:
        # Remove user profile cache
        await redis_client.delete(f"user_profile:{event.entity_id}")


async def handle_order_events(event: Event):
    """Handle order-related events"""
    if event.event_type == EventType.ORDER_CREATED.value:
        # Create order summary cache
        await redis_client.setex(
            f"order_summary:{event.entity_id}",
            1800,
            json.dumps(event.data, default=str)
        )

    elif event.event_type == EventType.ORDER_UPDATED.value:
        # Update order summary cache
        await redis_client.setex(
            f"order_summary:{event.entity_id}",
            1800,
            json.dumps(event.data, default=str)
        )
