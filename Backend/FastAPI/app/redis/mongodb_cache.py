"""
MongoDB + Redis Integration - Advanced Aggregation Caching
Real MongoDB integration with intelligent aggregation caching
"""
import asyncio
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .client import get_redis_client


class MongoDBCacheManager:
    """Advanced MongoDB aggregation caching with Redis"""

    def __init__(self, connection_string: str = None):
        self.redis_client = get_redis_client()
        self.connection_string = connection_string or "mongodb://localhost:27017/sec_cc"
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.cache_prefix = "mongodb_cache"

        # Performance statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "aggregations_executed": 0,
            "cache_invalidations": 0,
            "errors": 0
        }

    async def initialize(self, database_name: str = "sec_cc"):
        """Initialize MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.database = self.client[database_name]

            # Test connection
            await self.client.admin.command('ping')
            print("✅ MongoDB connection established")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise

    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    def _generate_aggregation_key(self, collection: str, pipeline: List[Dict], params: Dict = None) -> str:
        """Generate unique cache key for aggregation"""
        key_data = {
            "collection": collection,
            "pipeline": pipeline,
            "params": params or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_key}"

    def _generate_query_key(self, collection: str, query: Dict, params: Dict = None) -> str:
        """Generate unique cache key for query"""
        key_data = {
            "collection": collection,
            "query": query,
            "params": params or {}
        }

        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_key}"

    async def _get_collection_dependencies(self, collection: str, pipeline: List[Dict] = None) -> List[str]:
        """Extract collection dependencies from aggregation pipeline"""
        dependencies = [collection]

        if pipeline:
            for stage in pipeline:
                # Look for $lookup stages
                if "$lookup" in stage:
                    lookup_collection = stage["$lookup"].get("from")
                    if lookup_collection:
                        dependencies.append(lookup_collection)

        return dependencies

    async def cached_aggregation(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]],
        params: Dict = None,
        ttl: int = 600,
        force_refresh: bool = False,
        max_documents: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Execute MongoDB aggregation with intelligent caching
        """
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_aggregation_key(collection, pipeline, params)

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = await self.redis_client.get(cache_key)
            if cached_result:
                cache_info = json.loads(cached_result)

                # Check if cache is expired
                if time.time() - cache_info.get("cached_at", 0) < ttl:
                    self.stats["cache_hits"] += 1
                    return cache_info["result"]

        self.stats["cache_misses"] += 1

        # Execute aggregation
        try:
            collection_obj = self.database[collection]

            # Add $limit if not present and max_documents specified
            pipeline_with_limit = pipeline.copy()
            has_limit = any(stage.get("$limit") for stage in pipeline_with_limit)

            if not has_limit and max_documents > 0:
                pipeline_with_limit.append({"$limit": max_documents})

            cursor = collection_obj.aggregate(pipeline_with_limit)
            documents = await cursor.to_list(length=None)

            # Convert ObjectId and other MongoDB types to JSON serializable
            result = []
            for doc in documents:
                # Convert MongoDB document to dict and handle ObjectId
                doc_dict = {}
                for key, value in doc.items():
                    if hasattr(value, '__str__'):  # ObjectId, etc.
                        doc_dict[key] = str(value)
                    else:
                        doc_dict[key] = value
                result.append(doc_dict)

            # Get collection dependencies for invalidation
            collection_dependencies = await self._get_collection_dependencies(collection, pipeline)

            # Cache the result
            cache_data = {
                "result": result,
                "cached_at": time.time(),
                "ttl": ttl,
                "collection_dependencies": collection_dependencies,
                "pipeline": pipeline,
                "execution_time": time.time() - start_time,
                "document_count": len(result)
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            # Store in collection dependency sets for invalidation
            for coll in collection_dependencies:
                await self.redis_client.sadd(f"{self.cache_prefix}:collection:{coll}", cache_key)

            self.stats["aggregations_executed"] += 1
            return result

        except Exception as e:
            self.stats["errors"] += 1
            print(f"MongoDB aggregation error: {e}")
            raise

    async def cached_find_one(
        self,
        collection: str,
        query: Dict[str, Any],
        params: Dict = None,
        ttl: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Execute find_one with caching"""
        cache_key = self._generate_query_key(collection, query, params)

        # Check cache first
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            cache_info = json.loads(cached_result)

            if time.time() - cache_info.get("cached_at", 0) < ttl:
                self.stats["cache_hits"] += 1
                return cache_info["result"]

        self.stats["cache_misses"] += 1

        try:
            collection_obj = self.database[collection]
            document = await collection_obj.find_one(query)

            if document:
                # Convert MongoDB document
                result = {}
                for key, value in document.items():
                    if hasattr(value, '__str__'):
                        result[key] = str(value)
                    else:
                        result[key] = value

                # Cache the result
                cache_data = {
                    "result": result,
                    "cached_at": time.time(),
                    "ttl": ttl
                }

                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cache_data, default=str)
                )

                return result

            return None

        except Exception as e:
            self.stats["errors"] += 1
            print(f"MongoDB find_one error: {e}")
            raise

    async def cached_find(
        self,
        collection: str,
        query: Dict[str, Any],
        params: Dict = None,
        ttl: int = 300,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Execute find with caching"""
        cache_key = self._generate_query_key(collection, query, {**params, "limit": limit} if params else {"limit": limit})

        # Check cache first
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            cache_info = json.loads(cached_result)

            if time.time() - cache_info.get("cached_at", 0) < ttl:
                self.stats["cache_hits"] += 1
                return cache_info["result"]

        self.stats["cache_misses"] += 1

        try:
            collection_obj = self.database[collection]
            cursor = collection_obj.find(query).limit(limit)
            documents = await cursor.to_list(length=None)

            result = []
            for doc in documents:
                doc_dict = {}
                for key, value in doc.items():
                    if hasattr(value, '__str__'):
                        doc_dict[key] = str(value)
                    else:
                        doc_dict[key] = value
                result.append(doc_dict)

            # Cache the result
            cache_data = {
                "result": result,
                "cached_at": time.time(),
                "ttl": ttl
            }

            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )

            return result

        except Exception as e:
            self.stats["errors"] += 1
            print(f"MongoDB find error: {e}")
            raise

    async def invalidate_collection_cache(self, collection: str) -> int:
        """Invalidate all cached queries for a specific collection"""
        try:
            collection_key = f"{self.cache_prefix}:collection:{collection}"
            cache_keys = await self.redis_client.smembers(collection_key)

            if cache_keys:
                # Delete all cached queries for this collection
                await self.redis_client.delete(*cache_keys)
                # Clean up the collection set
                await self.redis_client.delete(collection_key)

            self.stats["cache_invalidations"] += len(cache_keys)
            return len(cache_keys)
        except Exception as e:
            print(f"Collection invalidation error: {e}")
            return 0

    async def execute_write_operation(self, collection: str, operation: str, document: Dict, invalidate_cache: bool = True) -> str:
        """Execute write operation and invalidate related caches"""
        try:
            collection_obj = self.database[collection]

            if operation == "insert":
                result = await collection_obj.insert_one(document)
                action_id = str(result.inserted_id)
            elif operation == "update":
                result = await collection_obj.update_one(
                    {"_id": document.get("_id")},
                    {"$set": document}
                )
                action_id = str(document.get("_id"))
            elif operation == "delete":
                result = await collection_obj.delete_one({"_id": document.get("_id")})
                action_id = str(document.get("_id"))
            else:
                raise ValueError(f"Unknown operation: {operation}")

            # Invalidate collection cache if requested
            if invalidate_cache:
                await self.invalidate_collection_cache(collection)

            return action_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"MongoDB write operation error: {e}")
            raise

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache performance statistics"""
        total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_rate = (self.stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0

        # Get cache size information
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)
            total_size = sum(await self.redis_client.strlen(key) for key in keys[:100])  # Sample

            return {
                "cache_hits": self.stats["cache_hits"],
                "cache_misses": self.stats["cache_misses"],
                "aggregations_executed": self.stats["aggregations_executed"],
                "cache_invalidations": self.stats["cache_invalidations"],
                "errors": self.stats["errors"],
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "estimated_cache_size_bytes": total_size,
                "cached_operations": len(keys),
                "performance_improvement": f"{round(hit_rate, 1)}%"
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_collection_cache_info(self, collection: str) -> Dict[str, Any]:
        """Get cache information for specific collection"""
        try:
            collection_key = f"{self.cache_prefix}:collection:{collection}"
            cache_keys = await self.redis_client.smembers(collection_key)

            return {
                "collection": collection,
                "cached_operations": len(cache_keys),
                "cache_keys": list(cache_keys)[:10]  # First 10 for preview
            }
        except Exception as e:
            return {"error": str(e)}


# Global MongoDB cache manager instance
mongodb_cache_manager = MongoDBCacheManager()
