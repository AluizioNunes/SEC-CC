"""
Event-Driven Architecture Implementation
Complete event-driven system with sagas and asynchronous processing
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from ..Redis.client import get_redis_client
from ..Message_Broker.message_broker import hybrid_broker


class EventType(Enum):
    """Event type enumeration"""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    ORDER_COMPLETED = "order_completed"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    INVENTORY_UPDATED = "inventory_updated"
    NOTIFICATION_SENT = "notification_sent"
    SYSTEM_ALERT = "system_alert"
    DATA_EXPORTED = "data_exported"
    REPORT_GENERATED = "report_generated"


class SagaStatus(Enum):
    """Saga status enumeration"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: float
    source_service: str
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Saga:
    """Saga transaction"""
    saga_id: str
    saga_type: str
    steps: List[Dict[str, Any]]
    current_step: int
    status: SagaStatus
    correlation_id: str
    created_at: float
    updated_at: float
    payload: Dict[str, Any]


class EventDrivenSystem:
    """Advanced event-driven architecture with saga patterns"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.event_prefix = "event_driven"

        # Event handlers
        self.event_handlers: Dict[EventType, List[Callable]] = {}

        # Saga coordinators
        self.saga_coordinators: Dict[str, Any] = {}

        # Event statistics
        self.stats = {
            "events_published": 0,
            "events_consumed": 0,
            "sagas_started": 0,
            "sagas_completed": 0,
            "sagas_failed": 0,
            "errors": 0
        }

    async def initialize(self) -> bool:
        """Initialize event-driven system"""
        try:
            # Start event consumers
            asyncio.create_task(self.consume_events())

            # Start saga coordinator
            asyncio.create_task(self.coordinate_sagas())

            print("✅ Event-Driven System initialized")
            return True

        except Exception as e:
            print(f"❌ Event-Driven System initialization failed: {e}")
            return False

    async def publish_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source_service: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish event to system"""
        try:
            event_id = str(uuid.uuid4())

            event = Event(
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                timestamp=time.time(),
                source_service=source_service,
                correlation_id=correlation_id,
                metadata=metadata
            )

            # Store event in Redis
            await self.redis_client.setex(
                f"{self.event_prefix}:event:{event_id}",
                86400,  # 24 hours
                json.dumps(asdict(event), default=str)
            )

            # Add to event stream
            await self.redis_client.xadd(
                f"{self.event_prefix}:stream",
                asdict(event)
            )

            # Publish to message broker
            await hybrid_broker.publish_message(
                message=asdict(event),
                routing_key=event_type.value,
                stream_name="events"
            )

            self.stats["events_published"] += 1

            return event_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Event publishing error: {e}")
            raise

    async def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register event handler for event type"""
        try:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []

            self.event_handlers[event_type].append(handler)

        except Exception as e:
            print(f"Event handler registration error: {e}")

    async def consume_events(self):
        """Consume events from stream"""
        while True:
            try:
                # Read events from Redis stream
                events = await self.redis_client.xread(
                    {f"{self.event_prefix}:stream": "$"},
                    count=10,
                    block=5000  # 5 seconds
                )

                for stream_name, stream_events in events:
                    for event_id, event_data in stream_events:
                        try:
                            # Process event
                            await self.process_event(event_data)

                            # Acknowledge event
                            await self.redis_client.xack(
                                f"{self.event_prefix}:stream",
                                "event_group",
                                event_id
                            )

                            self.stats["events_consumed"] += 1

                        except Exception as e:
                            print(f"Event processing error: {e}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Event consumption error: {e}")
                await asyncio.sleep(5)

    async def process_event(self, event_data: Dict[str, Any]):
        """Process individual event"""
        try:
            event_type_str = event_data.get("event_type")
            if not event_type_str:
                return

            # Convert string to EventType enum
            try:
                event_type = EventType(event_type_str)
            except ValueError:
                print(f"Unknown event type: {event_type_str}")
                return

            # Get registered handlers
            handlers = self.event_handlers.get(event_type, [])

            # Execute all handlers
            for handler in handlers:
                try:
                    await handler(event_data)
                except Exception as e:
                    print(f"Event handler execution error: {e}")

        except Exception as e:
            print(f"Event processing error: {e}")

    async def start_saga(
        self,
        saga_type: str,
        steps: List[Dict[str, Any]],
        payload: Dict[str, Any]
    ) -> str:
        """Start new saga transaction"""
        try:
            saga_id = str(uuid.uuid4())
            correlation_id = str(uuid.uuid4())

            saga = Saga(
                saga_id=saga_id,
                saga_type=saga_type,
                steps=steps,
                current_step=0,
                status=SagaStatus.STARTED,
                correlation_id=correlation_id,
                created_at=time.time(),
                updated_at=time.time(),
                payload=payload
            )

            # Store saga in Redis
            await self.redis_client.setex(
                f"{self.event_prefix}:saga:{saga_id}",
                86400,  # 24 hours
                json.dumps(asdict(saga), default=str)
            )

            # Add to active sagas
            await self.redis_client.sadd(
                f"{self.event_prefix}:sagas:active",
                saga_id
            )

            self.stats["sagas_started"] += 1

            # Trigger first step
            await self.execute_saga_step(saga, 0)

            return saga_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Saga start error: {e}")
            raise

    async def execute_saga_step(self, saga: Saga, step_index: int):
        """Execute saga step"""
        try:
            if step_index >= len(saga.steps):
                # Saga completed
                await self.complete_saga(saga)
                return

            step = saga.steps[step_index]
            action = step.get("action")
            service = step.get("service")

            # Execute step (in production, would call actual services)
            print(f"Executing saga step {step_index}: {action} on {service}")

            # Update saga status
            saga.current_step = step_index
            saga.status = SagaStatus.IN_PROGRESS
            saga.updated_at = time.time()

            # Store updated saga
            await self.redis_client.setex(
                f"{self.event_prefix}:saga:{saga.saga_id}",
                86400,
                json.dumps(asdict(saga), default=str)
            )

            # Simulate step execution
            await asyncio.sleep(0.1)

            # Move to next step
            await self.execute_saga_step(saga, step_index + 1)

        except Exception as e:
            print(f"Saga step execution error: {e}")
            await self.compensate_saga(saga)

    async def complete_saga(self, saga: Saga):
        """Complete saga successfully"""
        try:
            saga.status = SagaStatus.COMPLETED
            saga.updated_at = time.time()

            # Store completed saga
            await self.redis_client.setex(
                f"{self.event_prefix}:saga:{saga.saga_id}",
                86400,
                json.dumps(asdict(saga), default=str)
            )

            # Remove from active sagas
            await self.redis_client.srem(
                f"{self.event_prefix}:sagas:active",
                saga.saga_id
            )

            self.stats["sagas_completed"] += 1

            # Publish completion event
            await self.publish_event(
                EventType.SYSTEM_ALERT,
                {
                    "message": f"Saga {saga.saga_type} completed successfully",
                    "saga_id": saga.saga_id
                },
                "event_driven",
                saga.correlation_id
            )

        except Exception as e:
            print(f"Saga completion error: {e}")

    async def compensate_saga(self, saga: Saga):
        """Compensate failed saga"""
        try:
            saga.status = SagaStatus.FAILED
            saga.updated_at = time.time()

            # Store failed saga
            await self.redis_client.setex(
                f"{self.event_prefix}:saga:{saga.saga_id}",
                86400,
                json.dumps(asdict(saga), default=str)
            )

            # Remove from active sagas
            await self.redis_client.srem(
                f"{self.event_prefix}:sagas:active",
                saga.saga_id
            )

            self.stats["sagas_failed"] += 1

            # Execute compensation steps (in reverse order)
            for i in range(saga.current_step, -1, -1):
                step = saga.steps[i]
                compensation = step.get("compensation")
                service = step.get("service")

                if compensation:
                    print(f"Compensating step {i}: {compensation} on {service}")
                    # In production, would call actual compensation service

            # Update saga status to compensated
            saga.status = SagaStatus.COMPENSATED
            saga.updated_at = time.time()

            # Store compensated saga
            await self.redis_client.setex(
                f"{self.event_prefix}:saga:{saga.saga_id}",
                86400,
                json.dumps(asdict(saga), default=str)
            )

            # Publish failure event
            await self.publish_event(
                EventType.SYSTEM_ALERT,
                {
                    "message": f"Saga {saga.saga_type} failed and compensated",
                    "saga_id": saga.saga_id,
                    "failed_step": saga.current_step
                },
                "event_driven",
                saga.correlation_id
            )

        except Exception as e:
            print(f"Saga compensation error: {e}")

    async def coordinate_sagas(self):
        """Coordinate active sagas"""
        while True:
            try:
                # Get active sagas
                active_sagas = await self.redis_client.smembers(f"{self.event_prefix}:sagas:active")

                for saga_id in active_sagas:
                    # Get saga data
                    saga_data = await self.redis_client.get(f"{self.event_prefix}:saga:{saga_id}")
                    if saga_data:
                        saga = Saga(**json.loads(saga_data))

                        # Check if saga has timed out
                        if time.time() - saga.updated_at > 300:  # 5 minutes
                            print(f"Saga {saga_id} timed out")
                            await self.compensate_saga(saga)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Saga coordination error: {e}")
                await asyncio.sleep(60)

    async def get_event_statistics(self) -> Dict[str, Any]:
        """Get event-driven system statistics"""
        try:
            # Get recent events
            event_stream_info = await self.redis_client.xinfo_stream(f"{self.event_prefix}:stream")

            return {
                "event_stats": self.stats.copy(),
                "event_stream_info": event_stream_info,
                "active_sagas": await self.redis_client.scard(f"{self.event_prefix}:sagas:active"),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global event-driven system instance
event_driven_system = EventDrivenSystem()