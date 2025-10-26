"""
RabbitMQ + Redis Hybrid - Advanced Message Broker
Hybrid message broker with Redis Streams and RabbitMQ integration
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

import aio_pika
from ..Redis.client import get_redis_client


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
        self.rabbitmq_url = rabbitmq_url or "amqp://admin:admin123@rabbitmq:5672/"
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
        """Initialize both Redis and RabbitMQ connections (degrades gracefully if RabbitMQ is unavailable)"""
        # Try RabbitMQ; if not available, continue in Redis-only mode
        try:
            self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()

            # Declare main exchange
            await self.rabbitmq_channel.declare_exchange(
                'sec_cc_exchange',
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            print("✅ RabbitMQ connection established for hybrid broker")
        except Exception as e:
            # RabbitMQ not available; continue without it
            self.rabbitmq_connection = None
            self.rabbitmq_channel = None
            print(f"⚠️  RabbitMQ indisponível ({e}); seguindo em modo somente Redis")

        # Always consider Redis part initialized (client abstraction handles connectivity)
        print("✅ Redis Streams prontos para uso no broker híbrido")
        print("✅ Hybrid Message Broker inicializado" + (" (modo somente Redis)" if self.rabbitmq_channel is None else ""))

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
        message_id = f"msg_{int(time.time() * 1000)}"

        enriched_message = {
            "id": message_id,
            "timestamp": time.time(),
            "priority": priority.value,
            "routing_key": routing_key,
            "broker_type": broker_type.value,
            "data": message,
            "metadata": {
                "source": "backend",
                "version": "1.0",
                "retries": 0
            }
        }

        try:
            if broker_type == MessageBrokerType.REDIS:
                # Use Redis Streams
                return await self._publish_to_redis(enriched_message, stream_name or routing_key)

            elif broker_type == MessageBrokerType.RABBITMQ:
                # Use RabbitMQ only if channel is available
                if self.rabbitmq_channel is None:
                    # Fallback to Redis if RabbitMQ is unavailable
                    return await self._publish_to_redis(enriched_message, stream_name or routing_key)
                return await self._publish_to_rabbitmq(enriched_message, routing_key)

            else:  # HYBRID - Use both for redundancy
                redis_message_id = await self._publish_to_redis(enriched_message, stream_name or routing_key)

                # Also publish to RabbitMQ for critical messages, if available
                if self.rabbitmq_channel is not None and priority in [MessagePriority.HIGH, MessagePriority.CRITICAL]:
                    await self._publish_to_rabbitmq(enriched_message, routing_key)

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
                # Only consume from RabbitMQ if channel is available
                if self.rabbitmq_channel is None:
                    print("⚠️  RabbitMQ não disponível; consumo desabilitado para este broker")
                    return
                await self._consume_rabbitmq_queue(stream_name, callback, group_name)
            else:
                # Hybrid consumption
                tasks = [
                    self._consume_redis_stream(stream_name, callback, group_name, f"redis_{consumer_name}")
                ]
                if self.rabbitmq_channel is not None:
                    tasks.append(self._consume_rabbitmq_queue(stream_name, callback, group_name))
                await asyncio.gather(*tasks)

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
                    # Example: Set dead-letter exchange
                    # 'x-dead-letter-exchange': 'dlx_exchange'
                }
            )

            # Bind queue to exchange with routing key
            await queue.bind('sec_cc_exchange', routing_key or queue_name)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            # Decode message
                            payload = json.loads(message.body.decode())

                            # Process message
                            await callback(payload)

                            self.stats["messages_received"] += 1

                        except Exception as e:
                            print(f"RabbitMQ message processing error: {e}")

        except Exception as e:
            print(f"RabbitMQ queue consumption error: {e}")


# Export global broker instance
hybrid_broker = HybridMessageBroker()