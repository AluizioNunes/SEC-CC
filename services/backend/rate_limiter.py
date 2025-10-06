"""
Distributed Rate Limiting - Advanced DDoS Protection
Multiple rate limiting algorithms across distributed instances
"""
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum

from .client import get_redis_client


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class DistributedRateLimiter:
    """Advanced distributed rate limiting with multiple algorithms"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.rate_limit_prefix = "rate_limit"
        self.default_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }

        # Rate limit statistics
        self.stats = {
            "allowed": 0,
            "blocked": 0,
            "errors": 0
        }

    def _get_identifier_key(self, identifier: str, algorithm: str = "sliding_window") -> str:
        """Generate consistent key for rate limiting"""
        key_data = f"{identifier}:{algorithm}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.rate_limit_prefix}:{key_hash}"

    async def check_fixed_window(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 60
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Fixed window rate limiting
        Simple but can have burst issues at window boundaries
        """
        key = self._get_identifier_key(identifier, "fixed_window")
        current_time = int(time.time())

        try:
            # Get current window
            window_key = f"{key}:{current_time // window_seconds}"

            # Increment counter using Lua script for atomicity
            lua_script = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])

            local current = redis.call('INCR', key)
            if current == 1 then
                redis.call('EXPIRE', key, window)
            end

            return {current, limit - current + 1, window}
            """

            current_count, remaining, reset_in = await self.redis_client.eval(
                lua_script, 1, window_key, limit, window_seconds
            )

            if current_count > limit:
                self.stats["blocked"] += 1
                reset_time = (current_time // window_seconds + 1) * window_seconds
                return False, {
                    "algorithm": "fixed_window",
                    "limit": limit,
                    "current": current_count,
                    "remaining": 0,
                    "reset_in": reset_time - current_time,
                    "blocked": True
                }

            self.stats["allowed"] += 1
            return True, {
                "algorithm": "fixed_window",
                "limit": limit,
                "current": current_count,
                "remaining": remaining,
                "reset_in": window_seconds - (current_time % window_seconds),
                "blocked": False
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Fixed window rate limit error: {e}")
            return True, {"error": str(e)}

    async def check_sliding_window(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 60
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Sliding window rate limiting
        More accurate but more complex
        """
        key = self._get_identifier_key(identifier, "sliding_window")
        current_time = time.time()

        try:
            # Add current request timestamp
            await self.redis_client.zadd(key, {str(current_time): current_time})

            # Remove old entries outside window
            min_timestamp = current_time - window_seconds
            await self.redis_client.zremrangebyscore(key, 0, min_timestamp)

            # Set expiry for cleanup
            await self.redis_client.expire(key, window_seconds + 1)

            # Count requests in window
            current_count = await self.redis_client.zcard(key)

            if current_count > limit:
                # Calculate reset time (when oldest entry expires)
                oldest_entries = await self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    reset_time = oldest_entries[0][1] + window_seconds
                    self.stats["blocked"] += 1
                    return False, {
                        "algorithm": "sliding_window",
                        "limit": limit,
                        "current": current_count,
                        "remaining": 0,
                        "reset_in": int(reset_time - current_time),
                        "blocked": True
                    }

            self.stats["allowed"] += 1
            return True, {
                "algorithm": "sliding_window",
                "limit": limit,
                "current": current_count,
                "remaining": limit - current_count,
                "reset_in": window_seconds,
                "blocked": False
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Sliding window rate limit error: {e}")
            return True, {"error": str(e)}

    async def check_token_bucket(
        self,
        identifier: str,
        capacity: int,
        refill_rate: int,  # tokens per second
        window_seconds: int = 60
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Token bucket rate limiting
        Allows bursts but maintains average rate
        """
        key = self._get_identifier_key(identifier, "token_bucket")
        current_time = time.time()

        try:
            # Get current bucket state
            bucket_data = await self.redis_client.get(key)

            if bucket_data:
                bucket = json.loads(bucket_data)
            else:
                # Initialize new bucket
                bucket = {
                    "tokens": capacity,
                    "last_refill": current_time,
                    "capacity": capacity,
                    "refill_rate": refill_rate
                }

            # Refill tokens based on elapsed time
            time_elapsed = current_time - bucket["last_refill"]
            tokens_to_add = time_elapsed * refill_rate

            bucket["tokens"] = min(capacity, bucket["tokens"] + tokens_to_add)
            bucket["last_refill"] = current_time

            # Check if we have tokens for this request
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1

                # Save updated bucket
                await self.redis_client.setex(
                    key,
                    window_seconds,
                    json.dumps(bucket, default=str)
                )

                self.stats["allowed"] += 1
                return True, {
                    "algorithm": "token_bucket",
                    "limit": capacity,
                    "current": int(bucket["tokens"]),
                    "remaining": int(bucket["tokens"]),
                    "refill_rate": refill_rate,
                    "blocked": False
                }
            else:
                # Calculate when next token will be available
                next_token_time = (1 - bucket["tokens"]) / refill_rate
                self.stats["blocked"] += 1
                return False, {
                    "algorithm": "token_bucket",
                    "limit": capacity,
                    "current": int(bucket["tokens"]),
                    "remaining": 0,
                    "reset_in": int(next_token_time),
                    "refill_rate": refill_rate,
                    "blocked": True
                }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Token bucket rate limit error: {e}")
            return True, {"error": str(e)}

    async def check_multiple_limits(
        self,
        identifier: str,
        limits: Dict[str, int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check multiple rate limits simultaneously
        """
        if limits is None:
            limits = self.default_limits

        results = {}
        overall_allowed = True

        for limit_name, limit_value in limits.items():
            if limit_name == "requests_per_minute":
                allowed, info = await self.check_sliding_window(identifier, limit_value, 60)
            elif limit_name == "requests_per_hour":
                allowed, info = await self.check_sliding_window(identifier, limit_value, 3600)
            elif limit_name == "requests_per_day":
                allowed, info = await self.check_sliding_window(identifier, limit_value, 86400)
            else:
                continue

            results[limit_name] = info
            if not allowed:
                overall_allowed = False

        return overall_allowed, {
            "algorithm": "multiple_limits",
            "results": results,
            "overall_allowed": overall_allowed,
            "blocked": not overall_allowed
        }

    async def get_rate_limit_status(
        self,
        identifier: str,
        algorithm: str = "sliding_window"
    ) -> Dict[str, Any]:
        """Get current rate limit status for identifier"""
        key = self._get_identifier_key(identifier, algorithm)

        try:
            if algorithm == "fixed_window":
                # Get current window data - simplified for demo
                return {
                    "algorithm": algorithm,
                    "identifier": identifier,
                    "status": "active"
                }

            elif algorithm == "sliding_window":
                current_count = await self.redis_client.zcard(key)
                return {
                    "algorithm": algorithm,
                    "identifier": identifier,
                    "current_count": current_count,
                    "status": "active"
                }

            elif algorithm == "token_bucket":
                bucket_data = await self.redis_client.get(key)
                if bucket_data:
                    bucket = json.loads(bucket_data)
                    return {
                        "algorithm": algorithm,
                        "identifier": identifier,
                        "current_tokens": int(bucket["tokens"]),
                        "capacity": bucket["capacity"],
                        "refill_rate": bucket["refill_rate"],
                        "status": "active"
                    }

            return {"error": "Unknown algorithm"}
        except Exception as e:
            return {"error": str(e)}

    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        total_requests = self.stats["allowed"] + self.stats["blocked"]

        return {
            "allowed": self.stats["allowed"],
            "blocked": self.stats["blocked"],
            "total_requests": total_requests,
            "block_rate_percent": round((self.stats["blocked"] / total_requests * 100), 2) if total_requests > 0 else 0,
            "errors": self.stats["errors"]
        }


# Global rate limiter instance
rate_limiter = DistributedRateLimiter()
