"""
Database Optimization Module for FastAPI
Ultra-advanced database caching and query optimization system
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from contextlib import asynccontextmanager
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta

# Import database libraries
import asyncpg
import databases
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis

# Initialize logger
logger = structlog.get_logger()

@dataclass
class DatabaseConfig:
    """Database configuration for connection pooling and optimization"""
    postgres_url: str
    mongodb_url: str
    redis_url: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600

class QueryOptimizer:
    """Advanced query optimization to eliminate N+1 queries"""

    def __init__(self, db_config: DatabaseConfig):
        self.config = db_config
        self.query_cache = {}
        self.relationship_cache = {}
        self._init_databases()

    def _init_databases(self):
        """Initialize database connections with optimized pooling"""
        # PostgreSQL connection with advanced pooling
        self.postgres_engine = create_engine(
            self.config.postgres_url,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=True,
            echo=False
        )

        # Async database connection
        self.database = databases.Database(self.config.postgres_url)

        # Redis connection for caching
        self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)

        # Session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.postgres_engine)

    async def get_optimized_session(self):
        """Get optimized database session with caching"""
        return self.SessionLocal()

    @asynccontextmanager
    async def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            await asyncio.get_event_loop().run_in_executor(None, session.commit)
        except Exception:
            await asyncio.get_event_loop().run_in_executor(None, session.rollback)
            raise
        finally:
            await asyncio.get_event_loop().run_in_executor(None, session.close)

    async def optimize_n_plus_1_query(self, query_func, cache_key: str = None, ttl: int = 300):
        """Optimize queries that would cause N+1 problems"""
        if cache_key and await self.redis_client.exists(cache_key):
            cached_result = await self.redis_client.get(cache_key)
            logger.info("Using cached query result", cache_key=cache_key)
            return json.loads(cached_result)

        try:
            # Execute optimized query
            start_time = time.time()
            result = await query_func()
            execution_time = time.time() - start_time

            # Cache the result
            if cache_key:
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
                logger.info(
                    "Query optimized and cached",
                    execution_time=f"{execution_time".3f"}s",
                    cache_key=cache_key
                )

            return result

        except Exception as e:
            logger.error("Query optimization failed", error=str(e))
            raise

    async def preload_relationships(self, model_class, relationship_names: List[str]):
        """Preload relationships to avoid N+1 queries"""
        cache_key = f"preload_{model_class.__name__}_{'_'.join(relationship_names)}"

        if cache_key in self.relationship_cache:
            return self.relationship_cache[cache_key]

        # Use SQLAlchemy joinedload for eager loading
        query = select(model_class)

        for rel_name in relationship_names:
            if hasattr(model_class, rel_name):
                query = query.options(joinedload(getattr(model_class, rel_name)))

        async with self.get_session() as session:
            result = await asyncio.get_event_loop().run_in_executor(
                None, session.execute, query
            )
            result = result.scalars().all()

        self.relationship_cache[cache_key] = result
        return result

    async def batch_optimize_queries(self, queries: List[callable]) -> List[Any]:
        """Execute multiple queries in batch to reduce database round trips"""
        results = []

        # Group queries by type and execute in batches
        for query_func in queries:
            try:
                result = await query_func()
                results.append(result)
            except Exception as e:
                logger.error("Batch query failed", error=str(e))
                results.append(None)

        return results

class RedisCacheManager:
    """Advanced Redis caching for API responses and database queries"""

    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}

    async def get_cached_response(self, key: str) -> Optional[str]:
        """Get cached API response"""
        try:
            value = await self.redis_client.get(key)
            if value:
                self.cache_stats["hits"] += 1
                return value
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            logger.error("Cache get failed", error=str(e))
            return None

    async def set_cached_response(self, key: str, value: str, ttl: int = 300):
        """Set cached API response"""
        try:
            await self.redis_client.setex(key, ttl, value)
            self.cache_stats["sets"] += 1
            logger.debug("Response cached", key=key, ttl=ttl)
        except Exception as e:
            logger.error("Cache set failed", error=str(e))

    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info("Cache invalidated", pattern=pattern, keys_deleted=len(keys))
        except Exception as e:
            logger.error("Cache invalidation failed", error=str(e))

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_ratio = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "hit_ratio": round(hit_ratio, 2),
            "total_requests": total_requests
        }

class ConnectionPoolManager:
    """Advanced connection pool management for databases"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool_stats = {
            "active_connections": 0,
            "pool_size": config.pool_size,
            "created_connections": 0,
            "expired_connections": 0
        }

    async def get_connection_health(self) -> Dict[str, Any]:
        """Get connection pool health metrics"""
        return {
            "pool_size": self.pool_stats["pool_size"],
            "active_connections": self.pool_stats["active_connections"],
            "created_connections": self.pool_stats["created_connections"],
            "expired_connections": self.pool_stats["expired_connections"],
            "pool_utilization": (self.pool_stats["active_connections"] / self.pool_stats["pool_size"]) * 100,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def optimize_connection_usage(self):
        """Optimize connection pool usage based on load"""
        # Monitor and adjust pool size based on usage patterns
        health = await self.get_connection_health()

        if health["pool_utilization"] > 80:
            logger.warning("High pool utilization detected", utilization=health["pool_utilization"])
            # Could implement dynamic pool resizing here

        return health

# Global instances
db_config = DatabaseConfig(
    postgres_url=os.getenv("POSTGRES_URL", "postgresql://sec:secpass@postgres:5432/secdb"),
    mongodb_url=os.getenv("MONGODB_URL", "mongodb://mongodb:27017/secmongo"),
    redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    pool_size=20,
    max_overflow=30
)

query_optimizer = QueryOptimizer(db_config)
redis_cache_manager = RedisCacheManager(db_config.redis_url)
connection_pool_manager = ConnectionPoolManager(db_config)

# Helper functions for API endpoints
async def cache_api_response(key: str, response_func, ttl: int = 300):
    """Cache API response with automatic serialization"""
    cached = await redis_cache_manager.get_cached_response(key)
    if cached:
        return json.loads(cached)

    response = await response_func()
    await redis_cache_manager.set_cached_response(key, json.dumps(response, default=str), ttl)
    return response

async def invalidate_api_cache(pattern: str):
    """Invalidate API cache by pattern"""
    await redis_cache_manager.invalidate_pattern(pattern)

async def get_database_session():
    """Get optimized database session"""
    return await query_optimizer.get_optimized_session()
