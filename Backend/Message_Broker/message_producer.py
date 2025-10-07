"""
Message Producer for FastAPI
Produces messages to the hybrid message broker for inter-service communication
"""
import asyncio
from typing import Dict, Any

from .message_handler import message_handler


class MessageProducer:
    """Message producer for sending messages to other services"""

    async def send_user_created_event(self, user_id: str, user_data: Dict[str, Any]):
        """Send user created event to other services"""
        event_data = {
            "user_id": user_id,
            "user_data": user_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await message_handler.publish_event(
            event_type="user_created",
            data=event_data
        )

    async def send_order_created_event(self, order_id: str, order_data: Dict[str, Any]):
        """Send order created event to other services"""
        event_data = {
            "order_id": order_id,
            "order_data": order_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await message_handler.publish_event(
            event_type="order_created",
            data=event_data
        )

    async def send_payment_processed_event(self, payment_id: str, payment_data: Dict[str, Any]):
        """Send payment processed event to other services"""
        event_data = {
            "payment_id": payment_id,
            "payment_data": payment_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await message_handler.publish_event(
            event_type="payment_processed",
            data=event_data
        )

    async def send_notification_event(self, notification_type: str, recipient: str, message: str):
        """Send notification event to other services"""
        event_data = {
            "notification_type": notification_type,
            "recipient": recipient,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await message_handler.publish_event(
            event_type="notification_sent",
            data=event_data
        )


# Global message producer instance
message_producer = MessageProducer()