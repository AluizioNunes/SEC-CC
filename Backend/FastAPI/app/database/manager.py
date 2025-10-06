"""
Database integration module with Redis caching
"""
import os
import asyncpg
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict, Any, List
import json
import hashlib
import redis.asyncio as redis
from ..redis.database_cache import DatabaseCache
from ..redis.client import get_redis_client


class DatabaseManager:
    """Integrated database manager with Redis caching"""

    def __init__(self):
        # PostgreSQL connection
        self.postgres_url = os.getenv("POSTGRES_URL", "postgresql+asyncpg://sec:secpass@postgres:5432/secdb")
        self.postgres_engine = create_async_engine(self.postgres_url, echo=False)
        self.postgres_session = sessionmaker(
            bind=self.postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # MongoDB connection
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
        self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
        self.mongodb_db = self.mongodb_client.secmongo

        # Redis cache
        self.cache = DatabaseCache()
        self.redis_client = get_redis_client()

    async def init_postgres(self):
        """Initialize PostgreSQL connection"""
        try:
            # Test connection
            async with self.postgres_engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: None)
            print("✅ PostgreSQL connected successfully")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")

    async def init_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            # Test connection
            await self.mongodb_client.admin.command('ping')
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")

    # PostgreSQL operations with Redis cache
    async def get_cached_postgres_data(self, query_key: str, query_func, ttl: int = 300) -> Optional[Dict]:
        """Get data from PostgreSQL with Redis caching"""
        cache_key = f"postgres:{hashlib.md5(query_key.encode()).hexdigest()}"

        # Try cache first
        cached_data = await self.cache.get_cached_query("postgres", query_key, {})
        if cached_data:
            return cached_data

        # Execute query
        try:
            async with self.postgres_session() as session:
                result = await query_func(session)
                if result:
                    await self.cache.cache_query_result("postgres", query_key, {}, result, ttl)
                    return result
        except Exception as e:
            print(f"PostgreSQL query error: {e}")

        return None

    # MongoDB operations with Redis cache
    async def get_cached_mongodb_data(self, collection: str, query: Dict, ttl: int = 300) -> Optional[Dict]:
        """Get data from MongoDB with Redis caching"""
        query_str = json.dumps(query, sort_keys=True)
        cache_key = f"mongodb:{collection}:{hashlib.md5(query_str.encode()).hexdigest()}"

        # Try cache first
        cached_data = await self.cache.get_cached_query("mongodb", cache_key, query)
        if cached_data:
            return cached_data

        # Execute query
        try:
            result = await self.mongodb_db[collection].find_one(query)
            if result:
                await self.cache.cache_query_result("mongodb", cache_key, query, result, ttl)
                return result
        except Exception as e:
            print(f"MongoDB query error: {e}")

        return None

    # Combined operations
    async def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Get user data from PostgreSQL and MongoDB with Redis caching"""
        user_data = {}

        # Get user from PostgreSQL
        postgres_user = await self.get_cached_postgres_data(
            f"user_profile:{user_id}",
            lambda session: session.execute(
                "SELECT id, username, email, created_at FROM users WHERE id = :user_id",
                {"user_id": user_id}
            ).first(),
            ttl=600
        )

        if postgres_user:
            user_data.update({
                "id": postgres_user.id,
                "username": postgres_user.username,
                "email": postgres_user.email,
                "created_at": postgres_user.created_at.isoformat() if postgres_user.created_at else None
            })

        # Get user preferences from MongoDB
        mongodb_prefs = await self.get_cached_mongodb_data(
            "user_preferences",
            {"user_id": user_id},
            ttl=300
        )

        if mongodb_prefs:
            user_data["preferences"] = mongodb_prefs.get("preferences", {})

        return user_data if user_data else None

    async def create_user_with_cache(self, username: str, email: str, preferences: Dict = None) -> Dict:
        """Create user in PostgreSQL + MongoDB with Redis cache invalidation"""
        try:
            # Create in PostgreSQL
            async with self.postgres_session() as session:
                result = await session.execute(
                    "INSERT INTO users (username, email) VALUES (:username, :email) RETURNING id",
                    {"username": username, "email": email}
                )
                user_id = result.scalar()

                await session.commit()

            # Create in MongoDB
            await self.mongodb_db.user_preferences.insert_one({
                "user_id": user_id,
                "preferences": preferences or {}
            })

            # Invalidate related caches
            await self.cache.invalidate_table_cache("postgres", "users")
            await self.cache.invalidate_table_cache("mongodb", "user_preferences")

            return {"id": user_id, "username": username, "email": email}

        except Exception as e:
            print(f"User creation error: {e}")
            return {}

    async def close(self):
        """Close all connections"""
        await self.postgres_engine.dispose()
        self.mongodb_client.close()


# Global instance
db_manager = DatabaseManager()
