"""
Message Handler for FastAPI
Consumes messages from the hybrid message broker
"""
import asyncio
import json
from typing import Dict, Any, Callable

from .message_broker import hybrid_broker, MessageBrokerType


class MessageHandler:
    """Message handler for consuming messages from the hybrid broker"""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    async def initialize(self):
        """Initialize message handler"""
        try:
            # Start consuming messages from Redis Streams
            asyncio.create_task(self.consume_redis_messages())
            
            # Start consuming messages from RabbitMQ
            asyncio.create_task(self.consume_rabbitmq_messages())
            
            print("✅ Message handler initialized")
        except Exception as e:
            print(f"❌ Message handler initialization failed: {e}")

    async def register_handler(self, message_type: str, handler: Callable):
        """Register message handler for specific message type"""
        self.handlers[message_type] = handler

    async def consume_redis_messages(self):
        """Consume messages from Redis Streams"""
        async def redis_callback(message_data: Dict[str, Any]):
            try:
                # Extract message type from routing key or data
                message_type = message_data.get("routing_key", "default")
                
                # Get handler for message type
                handler = self.handlers.get(message_type)
                
                if handler:
                    await handler(message_data)
                else:
                    print(f"⚠️  No handler found for message type: {message_type}")
                    
            except Exception as e:
                print(f"❌ Error processing Redis message: {e}")

        # Consume messages from default stream
        await hybrid_broker.consume_messages(
            stream_name="default",
            callback=redis_callback,
            broker_type=MessageBrokerType.REDIS
        )

    async def consume_rabbitmq_messages(self):
        """Consume messages from RabbitMQ"""
        async def rabbitmq_callback(message_data: Dict[str, Any]):
            try:
                # Extract message type from routing key or data
                message_type = message_data.get("routing_key", "default")
                
                # Get handler for message type
                handler = self.handlers.get(message_type)
                
                if handler:
                    await handler(message_data)
                else:
                    print(f"⚠️  No handler found for message type: {message_type}")
                    
            except Exception as e:
                print(f"❌ Error processing RabbitMQ message: {e}")

        # Consume messages from default queue
        await hybrid_broker.consume_messages(
            stream_name="default",
            callback=rabbitmq_callback,
            broker_type=MessageBrokerType.RABBITMQ
        )

    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: str = "NORMAL"
    ):
        """Publish event to message broker"""
        try:
            message = {
                "event_type": event_type,
                "data": data,
                "source": "fastapi",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Publish to hybrid broker
            message_id = await hybrid_broker.publish_message(
                message=message,
                routing_key=event_type,
                stream_name=event_type
            )
            
            print(f"✅ Event {event_type} published with ID: {message_id}")
            return message_id
            
        except Exception as e:
            print(f"❌ Error publishing event: {e}")
            raise


# Global message handler instance
message_handler = MessageHandler()