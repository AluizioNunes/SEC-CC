"""
Redis distributed locks for concurrency control
"""
import time
import uuid
from typing import Optional, Any
from .client import get_redis_client

class DistributedLock:
    """Distributed lock implementation using Redis"""

    def __init__(self, name: str, ttl: int = 30):
        self.name = f"lock:{name}"
        self.ttl = ttl
        self.token = str(uuid.uuid4())
        self.redis_client = get_redis_client()

    async def acquire(self, timeout: int = 10) -> bool:
        """Acquire distributed lock"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Try to set lock with NX (only if not exists) and PX (milliseconds TTL)
            success = await self.redis_client.set(
                self.name,
                self.token,
                nx=True,
                px=self.ttl * 1000
            )

            if success:
                return True

            # Wait a bit before retrying
            await asyncio.sleep(0.1)

        return False

    async def release(self) -> bool:
        """Release distributed lock"""
        try:
            # Only release if we own the lock
            current_token = await self.redis_client.get(self.name)

            if current_token == self.token:
                await self.redis_client.delete(self.name)
                return True

            return False
        except Exception as e:
            print(f"Redis lock release error: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        success = await self.acquire()
        if not success:
            raise RuntimeError(f"Could not acquire lock: {self.name}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.release()

async def with_lock(lock_name: str, operation: Any, ttl: int = 30, timeout: int = 10):
    """Execute operation with distributed lock"""
    lock = DistributedLock(lock_name, ttl)

    async with lock:
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

async def increment_counter_safely(counter_name: str, increment: int = 1) -> int:
    """Safely increment counter using distributed lock"""
    async def _increment():
        redis_client = get_redis_client()
        current = await redis_client.get(counter_name)
        if current is None:
            new_value = increment
        else:
            new_value = int(current) + increment
        await redis_client.set(counter_name, str(new_value))
        return new_value

    return await with_lock(f"counter:{counter_name}", _increment)

async def update_user_balance(user_id: str, amount: float) -> bool:
    """Safely update user balance using distributed lock"""
    async def _update_balance():
        redis_client = get_redis_client()
        balance_key = f"user:balance:{user_id}"

        current_balance = await redis_client.get(balance_key)
        if current_balance is None:
            new_balance = amount
        else:
            new_balance = float(current_balance) + amount

        await redis_client.set(balance_key, str(new_balance))
        return True

    try:
        await with_lock(f"user:balance:{user_id}", _update_balance)
        return True
    except RuntimeError:
        return False

async def safe_inventory_update(product_id: str, quantity_change: int) -> bool:
    """Safely update inventory using distributed lock"""
    async def _update_inventory():
        redis_client = get_redis_client()
        inventory_key = f"product:inventory:{product_id}"

        current_inventory = await redis_client.get(inventory_key)
        if current_inventory is None:
            new_inventory = max(0, quantity_change)
        else:
            new_inventory = max(0, int(current_inventory) + quantity_change)

        await redis_client.set(inventory_key, str(new_inventory))
        return True

    try:
        await with_lock(f"product:inventory:{product_id}", _update_inventory)
        return True
    except RuntimeError:
        return False
