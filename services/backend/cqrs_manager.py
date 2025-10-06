"""
Advanced Event Sourcing - CQRS Pattern
Complete CQRS implementation with command and query separation
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

from .client import get_redis_client

T = TypeVar('T')


class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class Command:
    """Command data structure"""
    command_id: str
    command_type: str
    entity_id: str
    entity_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    status: CommandStatus
    created_at: float
    processed_at: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: str
    entity_id: str
    entity_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    version: int
    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None


class AggregateRoot(ABC):
    """Base class for aggregate roots in CQRS"""

    def __init__(self, entity_id: str, entity_type: str):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.version = 0
        self.uncommitted_events: List[Event] = []
        self.state = {}

    @abstractmethod
    def apply_event(self, event: Event) -> None:
        """Apply event to aggregate state"""
        pass

    def raise_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> None:
        """Raise new event"""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            data=data,
            metadata=metadata or {},
            timestamp=time.time(),
            version=self.version + 1
        )

        self.apply_event(event)
        self.uncommitted_events.append(event)

    def get_uncommitted_events(self) -> List[Event]:
        """Get events that haven't been committed yet"""
        return self.uncommitted_events.copy()

    def mark_events_as_committed(self) -> None:
        """Mark all events as committed"""
        self.uncommitted_events.clear()
        self.version += len(self.uncommitted_events)


class CommandHandler(ABC):
    """Base class for command handlers"""

    @abstractmethod
    async def handle(self, command: Command) -> Any:
        """Handle command and return result"""
        pass


class EventHandler(ABC):
    """Base class for event handlers"""

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle event"""
        pass


class CQRSManager:
    """Advanced CQRS implementation with Redis Streams"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.cqrs_prefix = "cqrs"

        # CQRS statistics
        self.stats = {
            "commands_processed": 0,
            "events_published": 0,
            "events_consumed": 0,
            "aggregates_loaded": 0,
            "errors": 0
        }

        # Registered handlers
        self.command_handlers: Dict[str, CommandHandler] = {}
        self.event_handlers: Dict[str, List[EventHandler]] = defaultdict(list)

    def register_command_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register command handler"""
        self.command_handlers[command_type] = handler

    def register_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register event handler"""
        self.event_handlers[event_type].append(handler)

    async def execute_command(self, command_type: str, entity_id: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """Execute command and return command ID"""
        command_id = str(uuid.uuid4())

        command = Command(
            command_id=command_id,
            command_type=command_type,
            entity_id=entity_id,
            entity_type=data.get("entity_type", "unknown"),
            data=data,
            metadata=metadata or {},
            status=CommandStatus.PENDING,
            created_at=time.time()
        )

        try:
            # Store command
            await self.redis_client.setex(
                f"{self.cqrs_prefix}:command:{command_id}",
                86400 * 7,  # 7 days
                json.dumps(asdict(command), default=str)
            )

            # Update command status to processing
            command.status = CommandStatus.PROCESSING
            await self.redis_client.setex(
                f"{self.cqrs_prefix}:command:{command_id}",
                86400 * 7,
                json.dumps(asdict(command), default=str)
            )

            # Get command handler
            handler = self.command_handlers.get(command_type)
            if not handler:
                raise ValueError(f"No handler registered for command type: {command_type}")

            # Execute command
            result = await handler.handle(command)

            # Update command status to completed
            command.status = CommandStatus.COMPLETED
            command.processed_at = time.time()
            await self.redis_client.setex(
                f"{self.cqrs_prefix}:command:{command_id}",
                86400 * 7,
                json.dumps(asdict(command), default=str)
            )

            self.stats["commands_processed"] += 1
            return command_id

        except Exception as e:
            self.stats["errors"] += 1

            # Update command status to failed
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            command.processed_at = time.time()

            await self.redis_client.setex(
                f"{self.cqrs_prefix}:command:{command_id}",
                86400 * 7,
                json.dumps(asdict(command), default=str)
            )

            raise

    async def publish_event(self, event_type: str, entity_id: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """Publish event to event store"""
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            entity_id=entity_id,
            entity_type=data.get("entity_type", "unknown"),
            data=data,
            metadata=metadata or {},
            timestamp=time.time(),
            version=1  # Would be incremented in real implementation
        )

        try:
            # Store in event store (main stream)
            main_stream = f"{self.cqrs_prefix}:events:main"
            await self.redis_client.xadd(main_stream, asdict(event))

            # Store in entity-specific stream
            entity_stream = f"{self.cqrs_prefix}:events:entity:{event.entity_type}:{entity_id}"
            await self.redis_client.xadd(entity_stream, asdict(event))

            # Process event with registered handlers
            await self.process_event(event)

            self.stats["events_published"] += 1
            return event.event_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Event publishing error: {e}")
            raise

    async def process_event(self, event: Event) -> None:
        """Process event with registered handlers"""
        try:
            handlers = self.event_handlers.get(event.event_type, [])

            for handler in handlers:
                try:
                    await handler.handle(event)
                    self.stats["events_consumed"] += 1
                except Exception as e:
                    print(f"Event handler error for {event.event_type}: {e}")

        except Exception as e:
            print(f"Event processing error: {e}")

    async def load_aggregate(self, entity_type: str, entity_id: str) -> Optional[AggregateRoot]:
        """Load aggregate from event store"""
        try:
            # Get entity events
            entity_stream = f"{self.cqrs_prefix}:events:entity:{entity_type}:{entity_id}"
            events_data = await self.redis_client.xrange(entity_stream, min="-", max="+")

            if not events_data:
                return None

            # Create aggregate instance (would use factory pattern in real implementation)
            aggregate = self.create_aggregate_instance(entity_type, entity_id)

            # Apply events to rebuild state
            for event_id, event_data in events_data:
                event = Event(**event_data)
                aggregate.apply_event(event)

            aggregate.version = len(events_data)
            self.stats["aggregates_loaded"] += 1

            return aggregate

        except Exception as e:
            print(f"Aggregate loading error: {e}")
            return None

    def create_aggregate_instance(self, entity_type: str, entity_id: str) -> AggregateRoot:
        """Create aggregate instance (factory pattern)"""
        # This would be implemented with a registry of aggregate types
        # For now, return a generic aggregate
        return GenericAggregate(entity_id, entity_type)

    async def replay_events(
        self,
        entity_type: str,
        entity_id: str,
        start_time: float = 0,
        end_time: float = None
    ) -> List[Event]:
        """Replay events for debugging or recovery"""
        try:
            entity_stream = f"{self.cqrs_prefix}:events:entity:{entity_type}:{entity_id}"

            if end_time is None:
                end_time = time.time()

            events_data = await self.redis_client.xrange(
                entity_stream,
                min=f"{start_time}",
                max=f"{end_time}"
            )

            events = [Event(**event_data) for event_id, event_data in events_data]
            return events

        except Exception as e:
            print(f"Event replay error: {e}")
            return []

    async def get_projection(self, projection_name: str) -> Optional[Dict[str, Any]]:
        """Get read projection"""
        try:
            projection_key = f"{self.cqrs_prefix}:projections:{projection_name}"
            projection_data = await self.redis_client.get(projection_key)

            if projection_data:
                return json.loads(projection_data)
            return None

        except Exception as e:
            print(f"Projection retrieval error: {e}")
            return None

    async def update_projection(self, projection_name: str, data: Dict[str, Any]) -> None:
        """Update read projection"""
        try:
            projection_key = f"{self.cqrs_prefix}:projections:{projection_name}"
            await self.redis_client.setex(
                projection_key,
                3600,  # 1 hour
                json.dumps(data, default=str)
            )
        except Exception as e:
            print(f"Projection update error: {e}")

    async def get_cqrs_stats(self) -> Dict[str, Any]:
        """Get CQRS system statistics"""
        try:
            # Get stream information
            pattern = f"{self.cqrs_prefix}:events:*"
            streams = await self.redis_client.keys(pattern)

            stream_info = {}
            total_events = 0

            for stream in streams:
                length = await self.redis_client.xlen(stream)
                total_events += length
                stream_info[stream] = {"length": length}

            return {
                "commands_processed": self.stats["commands_processed"],
                "events_published": self.stats["events_published"],
                "events_consumed": self.stats["events_consumed"],
                "aggregates_loaded": self.stats["aggregates_loaded"],
                "errors": self.stats["errors"],
                "total_events": total_events,
                "event_streams": stream_info,
                "registered_handlers": {
                    "command_handlers": len(self.command_handlers),
                    "event_handlers": {event_type: len(handlers) for event_type, handlers in self.event_handlers.items()}
                }
            }

        except Exception as e:
            return {"error": str(e)}


class GenericAggregate(AggregateRoot):
    """Generic aggregate root for demonstration"""

    def apply_event(self, event: Event) -> None:
        """Apply event to generic aggregate state"""
        self.state.update(event.data)
        self.version = event.version


# Global CQRS manager
cqrs_manager = CQRSManager()


# Example command handlers
class UserCommandHandler(CommandHandler):
    """Command handler for user operations"""

    async def handle(self, command: Command) -> Any:
        """Handle user commands"""
        if command.command_type == "CreateUser":
            # Create user logic
            user_data = command.data

            # Publish user created event
            await cqrs_manager.publish_event(
                "UserCreated",
                {"user_id": command.entity_id, **user_data},
                entity_id=command.entity_id,
                entity_type="User"
            )

            return {"user_id": command.entity_id, "status": "created"}

        elif command.command_type == "UpdateUser":
            # Update user logic
            user_data = command.data

            # Publish user updated event
            await cqrs_manager.publish_event(
                "UserUpdated",
                {"user_id": command.entity_id, **user_data},
                entity_id=command.entity_id,
                entity_type="User"
            )

            return {"user_id": command.entity_id, "status": "updated"}

        return {"error": "Unknown command type"}


class OrderCommandHandler(CommandHandler):
    """Command handler for order operations"""

    async def handle(self, command: Command) -> Any:
        """Handle order commands"""
        if command.command_type == "CreateOrder":
            # Create order logic
            order_data = command.data

            # Publish order created event
            await cqrs_manager.publish_event(
                "OrderCreated",
                {"order_id": command.entity_id, **order_data},
                entity_id=command.entity_id,
                entity_type="Order"
            )

            return {"order_id": command.entity_id, "status": "created"}

        return {"error": "Unknown command type"}


# Register default handlers
cqrs_manager.register_command_handler("CreateUser", UserCommandHandler())
cqrs_manager.register_command_handler("UpdateUser", UserCommandHandler())
cqrs_manager.register_command_handler("CreateOrder", OrderCommandHandler())


# Example event handlers
class UserEventHandler(EventHandler):
    """Event handler for user events"""

    async def handle(self, event: Event) -> None:
        """Handle user events"""
        if event.event_type == "UserCreated":
            # Update user projection
            user_projection = {
                "user_id": event.entity_id,
                "status": "active",
                **event.data
            }

            await cqrs_manager.update_projection("users", user_projection)

        elif event.event_type == "UserUpdated":
            # Update user projection
            user_projection = await cqrs_manager.get_projection("users") or {}
            user_projection.update(event.data)
            await cqrs_manager.update_projection("users", user_projection)


class OrderEventHandler(EventHandler):
    """Event handler for order events"""

    async def handle(self, event: Event) -> None:
        """Handle order events"""
        if event.event_type == "OrderCreated":
            # Update order projection
            order_projection = {
                "order_id": event.entity_id,
                "status": "pending",
                **event.data
            }

            await cqrs_manager.update_projection("orders", order_projection)


# Register default event handlers
cqrs_manager.register_event_handler("UserCreated", UserEventHandler())
cqrs_manager.register_event_handler("UserUpdated", UserEventHandler())
cqrs_manager.register_event_handler("OrderCreated", OrderEventHandler())
