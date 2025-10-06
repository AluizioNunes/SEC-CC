"""
Redis Advanced Data Structures
Utilitários para estruturas de dados avançadas do Redis
"""
import json
import time
from typing import Dict, Any, List, Optional, Set

from .client import get_redis_client


class RedisDataStructures:
    """Advanced Redis Data Structures Manager"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.ds_prefix = "data_structures"

    # Hash operations
    async def hash_set(self, key: str, field: str, value: Any) -> bool:
        """Set field in hash"""
        try:
            return await self.redis_client.hset(f"{self.ds_prefix}:hash:{key}", field, json.dumps(value))
        except Exception as e:
            print(f"Hash set error: {e}")
            return False

    async def hash_get(self, key: str, field: str) -> Optional[Any]:
        """Get field from hash"""
        try:
            value = await self.redis_client.hget(f"{self.ds_prefix}:hash:{key}", field)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Hash get error: {e}")
            return None

    async def hash_get_all(self, key: str) -> Dict[str, Any]:
        """Get all fields from hash"""
        try:
            values = await self.redis_client.hgetall(f"{self.ds_prefix}:hash:{key}")
            return {k: json.loads(v) for k, v in values.items()}
        except Exception as e:
            print(f"Hash get all error: {e}")
            return {}

    # Set operations
    async def set_add(self, key: str, *members: Any) -> int:
        """Add members to set"""
        try:
            json_members = [json.dumps(member) for member in members]
            return await self.redis_client.sadd(f"{self.ds_prefix}:set:{key}", *json_members)
        except Exception as e:
            print(f"Set add error: {e}")
            return 0

    async def set_members(self, key: str) -> Set[Any]:
        """Get all members from set"""
        try:
            members = await self.redis_client.smembers(f"{self.ds_prefix}:set:{key}")
            return {json.loads(member) for member in members}
        except Exception as e:
            print(f"Set members error: {e}")
            return set()

    async def set_is_member(self, key: str, member: Any) -> bool:
        """Check if member is in set"""
        try:
            json_member = json.dumps(member)
            return await self.redis_client.sismember(f"{self.ds_prefix}:set:{key}", json_member)
        except Exception as e:
            print(f"Set is member error: {e}")
            return False

    # Sorted Set operations (Leaderboards, etc.)
    async def sorted_set_add(self, key: str, member: Any, score: float) -> bool:
        """Add member to sorted set with score"""
        try:
            json_member = json.dumps(member)
            return await self.redis_client.zadd(f"{self.ds_prefix}:zset:{key}", {json_member: score})
        except Exception as e:
            print(f"Sorted set add error: {e}")
            return False

    async def sorted_set_get_range(self, key: str, start: int = 0, stop: int = -1) -> List[Dict[str, Any]]:
        """Get range from sorted set"""
        try:
            results = await self.redis_client.zrange(f"{self.ds_prefix}:zset:{key}", start, stop, withscores=True)
            return [{"member": json.loads(member), "score": score} for member, score in results]
        except Exception as e:
            print(f"Sorted set get range error: {e}")
            return []

    async def sorted_set_increment_score(self, key: str, member: Any, increment: float) -> float:
        """Increment score of member in sorted set"""
        try:
            json_member = json.dumps(member)
            new_score = await self.redis_client.zincrby(f"{self.ds_prefix}:zset:{key}", increment, json_member)
            return new_score
        except Exception as e:
            print(f"Sorted set increment error: {e}")
            return 0

    # List operations (Queues, etc.)
    async def list_push(self, key: str, *values: Any) -> int:
        """Push values to list (RPUSH)"""
        try:
            json_values = [json.dumps(value) for value in values]
            return await self.redis_client.rpush(f"{self.ds_prefix}:list:{key}", *json_values)
        except Exception as e:
            print(f"List push error: {e}")
            return 0

    async def list_pop(self, key: str) -> Optional[Any]:
        """Pop value from list (LPOP)"""
        try:
            value = await self.redis_client.lpop(f"{self.ds_prefix}:list:{key}")
            return json.loads(value) if value else None
        except Exception as e:
            print(f"List pop error: {e}")
            return None

    async def list_length(self, key: str) -> int:
        """Get list length"""
        try:
            return await self.redis_client.llen(f"{self.ds_prefix}:list:{key}")
        except Exception as e:
            print(f"List length error: {e}")
            return 0

    # HyperLogLog (Cardinality estimation)
    async def hyperloglog_add(self, key: str, *elements: Any) -> bool:
        """Add elements to HyperLogLog"""
        try:
            return await self.redis_client.pfadd(f"{self.ds_prefix}:hll:{key}", *elements)
        except Exception as e:
            print(f"HyperLogLog add error: {e}")
            return False

    async def hyperloglog_count(self, key: str) -> int:
        """Get approximate count from HyperLogLog"""
        try:
            return await self.redis_client.pfcount(f"{self.ds_prefix}:hll:{key}")
        except Exception as e:
            print(f"HyperLogLog count error: {e}")
            return 0

    # Geospatial operations
    async def geo_add(self, key: str, longitude: float, latitude: float, member: str) -> bool:
        """Add geospatial data"""
        try:
            return await self.redis_client.geoadd(f"{self.ds_prefix}:geo:{key}", longitude, latitude, member)
        except Exception as e:
            print(f"Geo add error: {e}")
            return False

    async def geo_search(self, key: str, longitude: float, latitude: float, radius_km: float, unit: str = "km") -> List[Dict[str, Any]]:
        """Search geospatial data within radius"""
        try:
            results = await self.redis_client.georadius(
                f"{self.ds_prefix}:geo:{key}",
                longitude, latitude, radius_km, unit=unit, withdist=True
            )
            return [{"member": member, "distance": distance} for member, distance in results]
        except Exception as e:
            print(f"Geo search error: {e}")
            return []


# Global data structures manager
redis_ds = RedisDataStructures()
