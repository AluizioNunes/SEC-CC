"""
RabbitMQ + Redis Hybrid - Advanced Message Broker
Hybrid message broker with Redis Streams and RabbitMQ integration
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

import aio_pika
from .client import get_redis_client


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class MessageBrokerType(Enum):
    """Message broker types"""
    RABBITMQ = "rabbitmq"
    REDIS = "redis"
    HYBRID = "hybrid"


class HybridMessageBroker:
    """Advanced hybrid message broker with RabbitMQ and Redis Streams"""

    def __init__(self, rabbitmq_url: str = None):
        self.redis_client = get_redis_client()
        self.rabbitmq_url = rabbitmq_url or "amqp://admin:admin123@localhost:5672/"
        self.rabbitmq_connection: Optional[aio_pika.Connection] = None
        self.rabbitmq_channel: Optional[aio_pika.Channel] = None
        self.redis_streams_prefix = "message_streams"

        # Message broker statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "redis_streams_messages": 0,
            "rabbitmq_messages": 0
        }

    async def initialize(self):
        """Initialize both Redis and RabbitMQ connections"""
        try:
            # Initialize RabbitMQ
            self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()

            # Declare main exchange
            await self.rabbitmq_channel.declare_exchange(
                'sec_cc_exchange',
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            print("✅ RabbitMQ + Redis hybrid broker initialized")
        except Exception as e:
            print(f"❌ Message broker initialization failed: {e}")
            raise

    async def close(self):
        """Close connections"""
        if self.rabbitmq_connection:
            await self.rabbitmq_connection.close()

    async def publish_message(
        self,
        message: Dict[str, Any],
        routing_key: str = "default",
        priority: MessagePriority = MessagePriority.NORMAL,
        broker_type: MessageBrokerType = MessageBrokerType.HYBRID,
        stream_name: str = None
    ) -> str:
        """
        Publish message to hybrid broker system
        """
        message_id = str(uuid.uuid4())
        timestamp = time.time()

        enriched_message = {
            "id": message_id,
            "timestamp": timestamp,
            "priority": priority.value,
            "routing_key": routing_key,
            "broker_type": broker_type.value,
            "data": message,
            "metadata": {
                "source": "fastapi",
                "version": "1.0",
                "retries": 0
            }
        }

        try:
            if broker_type == MessageBrokerType.REDIS:
                # Use Redis Streams
                return await self._publish_to_redis(enriched_message, stream_name or routing_key)

            elif broker_type == MessageBrokerType.RABBITMQ:
                # Use RabbitMQ
                return await self._publish_to_rabbitmq(enriched_message, routing_key)

            else:  # HYBRID - Use both for redundancy
                redis_message_id = await self._publish_to_redis(enriched_message, stream_name or routing_key)

                # Also publish to RabbitMQ for critical messages
                if priority in [MessagePriority.HIGH, MessagePriority.CRITICAL]:
                    rabbitmq_message_id = await self._publish_to_rabbitmq(enriched_message, routing_key)

                self.stats["messages_sent"] += 1
                return redis_message_id

        except Exception as e:
            self.stats["messages_failed"] += 1
            print(f"Message publish error: {e}")
            raise

    async def _publish_to_redis(self, message: Dict[str, Any], stream_name: str) -> str:
        """Publish message to Redis Streams"""
        try:
            stream_key = f"{self.redis_streams_prefix}:{stream_name}"

            message_id = await self.redis_client.xadd(
                stream_key,
                message
            )

            self.stats["redis_streams_messages"] += 1
            return message_id
        except Exception as e:
            print(f"Redis publish error: {e}")
            raise

    async def _publish_to_rabbitmq(self, message: Dict[str, Any], routing_key: str) -> str:
        """Publish message to RabbitMQ"""
        try:
            exchange = await self.rabbitmq_channel.get_exchange('sec_cc_exchange')

            message_body = json.dumps(message, default=str).encode()

            await exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    priority=message["priority"]
                ),
                routing_key=routing_key
            )

            self.stats["rabbitmq_messages"] += 1
            return message["id"]
        except Exception as e:
            print(f"RabbitMQ publish error: {e}")
            raise

    async def consume_messages(
        self,
        stream_name: str,
        callback: Callable,
        group_name: str = "default_group",
        consumer_name: str = None,
        broker_type: MessageBrokerType = MessageBrokerType.REDIS
    ):
        """Consume messages from hybrid broker"""
        if not consumer_name:
            consumer_name = f"consumer_{int(time.time())}"

        try:
            if broker_type == MessageBrokerType.REDIS:
                await self._consume_redis_stream(stream_name, callback, group_name, consumer_name)
            elif broker_type == MessageBrokerType.RABBITMQ:
                await self._consume_rabbitmq_queue(stream_name, callback, group_name)
            else:
                # Hybrid consumption
                await asyncio.gather(
                    self._consume_redis_stream(stream_name, callback, group_name, f"redis_{consumer_name}"),
                    self._consume_rabbitmq_queue(stream_name, callback, group_name)
                )

        except Exception as e:
            print(f"Message consumption error: {e}")
            raise

    async def _consume_redis_stream(
        self,
        stream_name: str,
        callback: Callable,
        group_name: str,
        consumer_name: str
    ):
        """Consume from Redis Streams"""
        stream_key = f"{self.redis_streams_prefix}:{stream_name}"

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
                                # Process message
                                await callback(message_data)

                                # Acknowledge message
                                await self.redis_client.xack(stream_key, group_name, message_id)

                                self.stats["messages_received"] += 1

                            except Exception as e:
                                print(f"Message processing error: {e}")

                except asyncio.TimeoutError:
                    continue  # No messages, continue waiting
                except Exception as e:
                    print(f"Redis stream consumption error: {e}")
                    await asyncio.sleep(5)  # Wait before retrying

        except Exception as e:
            print(f"Redis stream setup error: {e}")

    async def _consume_rabbitmq_queue(self, queue_name: str, callback: Callable, routing_key: str = ""):
        """Consume from RabbitMQ queue"""
        try:
            # Declare queue
            queue = await self.rabbitmq_channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 4
                }
            )

            # Bind to exchange
            exchange = await self.rabbitmq_channel.get_exchange('sec_cc_exchange')
            await queue.bind(exchange, routing_key)

            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        message_data = json.loads(message.body.decode())
                        await callback(message_data)
                        self.stats["messages_received"] += 1
                    except Exception as e:
                        print(f"RabbitMQ message processing error: {e}")

            # Start consuming
            await queue.consume(message_handler)

        except Exception as e:
            print(f"RabbitMQ queue setup error: {e}")

    async def create_dead_letter_queue(self, source_queue: str, max_retries: int = 3):
        """Create dead letter queue for failed messages"""
        try:
            dlq_name = f"{source_queue}_dlq"

            # Create DLQ
            dlq = await self.rabbitmq_channel.declare_queue(
                dlq_name,
                durable=True
            )

            # Configure source queue to route to DLQ after max retries
            await self.rabbitmq_channel.declare_queue(
                source_queue,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': '',
                    'x-dead-letter-routing-key': dlq_name,
                    'x-message-ttl': 60000,  # 1 minute
                    'x-max-retries': max_retries
                }
            )

            return dlq_name
        except Exception as e:
            print(f"Dead letter queue creation error: {e}")
            return None

    async def get_message_stats(self) -> Dict[str, Any]:
        """Get message broker statistics"""
        try:
            # Get Redis Streams info
            redis_info = await self._get_redis_streams_info()

            return {
                "messages_sent": self.stats["messages_sent"],
                "messages_received": self.stats["messages_received"],
                "messages_failed": self.stats["messages_failed"],
                "redis_streams_messages": self.stats["redis_streams_messages"],
                "rabbitmq_messages": self.stats["rabbitmq_messages"],
                "redis_streams_info": redis_info,
                "throughput_improvement": f"{round((self.stats['messages_sent'] / max(1, time.time() - asyncio.get_event_loop().time())) * 60, 1)}/min"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_redis_streams_info(self) -> Dict[str, Any]:
        """Get Redis Streams information"""
        try:
            pattern = f"{self.redis_streams_prefix}:*"
            streams = await self.redis_client.keys(pattern)

            info = {}
            for stream in streams:
                length = await self.redis_client.xlen(stream)
                info[stream] = {
                    "length": length,
                    "groups": await self._get_stream_groups(stream)
                }

            return info
        except Exception as e:
            return {"error": str(e)}

    async def _get_stream_groups(self, stream: str) -> Dict[str, Any]:
        """Get consumer groups for a stream"""
        try:
            groups = await self.redis_client.xinfo_groups(stream)
            return {group["name"]: group for group in groups}
        except Exception:
            return {}


# Global hybrid message broker instance
hybrid_broker = HybridMessageBroker()
