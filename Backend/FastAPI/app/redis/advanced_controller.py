"""
Redis Advanced Features Controller
Complete API for all Redis advanced features
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any, Optional, List

from .api_cache import (
    cache_response, get_cache_stats, invalidate_cache_by_tags,
    invalidate_cache_by_pattern, api_cache_manager
)
from .session_cluster import session_cluster
from .rate_limiter import rate_limiter
from .database_query_cache import db_cache_manager
from .data_structures import redis_ds

router = APIRouter(prefix="/redis-advanced", tags=["redis-advanced"])

# API Response Cache endpoints
@router.get("/cache/stats")
async def get_cache_stats_endpoint():
    """Get API response cache statistics"""
    return get_cache_stats()

@router.post("/cache/invalidate")
async def invalidate_cache_endpoint(tags: List[str] = None, pattern: str = None):
    """Invalidate cache by tags or pattern"""
    if tags:
        invalidated = await invalidate_cache_by_tags(tags)
        return {"invalidated_count": invalidated, "tags": tags, "method": "tags"}
    elif pattern:
        invalidated = await invalidate_cache_by_pattern(pattern)
        return {"invalidated_count": invalidated, "pattern": pattern, "method": "pattern"}
    else:
        raise HTTPException(status_code=400, detail="Tags or pattern required")

# Session Clustering endpoints
@router.post("/session/create")
async def create_session_endpoint(user_id: str, data: Dict[str, Any]):
    """Create distributed session"""
    session_id = await session_cluster.create_session(user_id, data)
    if not session_id:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return {"session_id": session_id, "user_id": user_id}

@router.get("/session/{session_id}")
async def get_session_endpoint(session_id: str):
    """Get session data"""
    session_data = await session_cluster.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_data

@router.get("/session/user/{user_id}")
async def get_user_session_endpoint(user_id: str):
    """Get user's current session"""
    session_data = await session_cluster.get_user_session(user_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="User session not found")

    return session_data

@router.put("/session/{session_id}")
async def update_session_endpoint(session_id: str, data: Dict[str, Any]):
    """Update session data"""
    success = await session_cluster.update_session(session_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or update failed")

    return {"success": True}

@router.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete session"""
    success = await session_cluster.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}

@router.get("/session/cluster/stats")
async def get_session_cluster_stats_endpoint():
    """Get session cluster statistics"""
    return await session_cluster.get_session_stats()

@router.post("/session/cleanup")
async def cleanup_expired_sessions_endpoint():
    """Clean up expired sessions"""
    cleaned = await session_cluster.cleanup_expired_sessions()
    return {"cleaned_sessions": cleaned}

# Rate Limiting endpoints
@router.get("/rate-limit/status")
async def get_rate_limit_status_endpoint(
    identifier: str,
    algorithm: str = "sliding_window"
):
    """Get rate limit status for identifier"""
    return await rate_limiter.get_rate_limit_status(identifier, algorithm)

@router.post("/rate-limit/test")
async def test_rate_limit_endpoint(
    identifier: str,
    limit: int = 5,
    algorithm: str = "sliding_window"
):
    """Test rate limiting (for development)"""
    if algorithm == "fixed_window":
        allowed, info = await rate_limiter.check_fixed_window(identifier, limit)
    elif algorithm == "sliding_window":
        allowed, info = await rate_limiter.check_sliding_window(identifier, limit)
    elif algorithm == "token_bucket":
        allowed, info = await rate_limiter.check_token_bucket(identifier, limit, 1)
    else:
        raise HTTPException(status_code=400, detail="Invalid algorithm")

    return {"allowed": allowed, "info": info}

@router.get("/rate-limit/stats")
async def get_rate_limit_stats_endpoint():
    """Get rate limiting statistics"""
    return rate_limiter.get_rate_limit_stats()

# Database Query Cache endpoints
@router.get("/database/cache/stats")
async def get_database_cache_stats_endpoint():
    """Get database query cache statistics"""
    return await db_cache_manager.get_cache_performance()

@router.post("/database/cache/invalidate")
async def invalidate_database_cache_endpoint(
    database: str = None,
    table: str = None,
    query_pattern: str = None
):
    """Invalidate database cache"""
    if not database:
        raise HTTPException(status_code=400, detail="Database required")

    if table:
        invalidated = await db_cache_manager.invalidate_table_data(database, table)
        return {
            "invalidated_count": invalidated,
            "database": database,
            "table": table,
            "method": "table"
        }
    elif query_pattern:
        invalidated = await db_cache_manager.query_cache.invalidate_query_cache(database, query_pattern)
        return {
            "invalidated_count": invalidated,
            "database": database,
            "query_pattern": query_pattern,
            "method": "query_pattern"
        }
    else:
        raise HTTPException(status_code=400, detail="Table or query pattern required")

# Data Structures endpoints
@router.post("/data-structures/hash/set")
async def hash_set_endpoint(key: str, field: str, value: Any):
    """Set hash field"""
    success = await redis_ds.hash_set(key, field, value)
    return {"success": success, "key": key, "field": field}

@router.get("/data-structures/hash/get")
async def hash_get_endpoint(key: str, field: str):
    """Get hash field"""
    value = await redis_ds.hash_get(key, field)
    if value is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"key": key, "field": field, "value": value}

@router.get("/data-structures/hash/all")
async def hash_get_all_endpoint(key: str):
    """Get all hash fields"""
    data = await redis_ds.hash_get_all(key)
    return {"key": key, "data": data}

@router.post("/data-structures/set/add")
async def set_add_endpoint(key: str, members: List[Any]):
    """Add members to set"""
    added = await redis_ds.set_add(key, *members)
    return {"added_count": added, "key": key, "members": members}

@router.get("/data-structures/set/members")
async def set_members_endpoint(key: str):
    """Get set members"""
    members = await redis_ds.set_members(key)
    return {"key": key, "members": list(members)}

@router.post("/data-structures/sorted-set/add")
async def sorted_set_add_endpoint(key: str, member: Any, score: float):
    """Add to sorted set"""
    success = await redis_ds.sorted_set_add(key, member, score)
    return {"success": success, "key": key, "member": member, "score": score}

@router.get("/data-structures/sorted-set/range")
async def sorted_set_get_range_endpoint(key: str, start: int = 0, stop: int = -1):
    """Get sorted set range"""
    results = await redis_ds.sorted_set_get_range(key, start, stop)
    return {"key": key, "results": results}

# Advanced demo endpoint with multiple Redis features
@router.get("/demo/{user_id}")
@cache_response(ttl=300, tags=["demo", "user"], vary_by_user=True)
async def advanced_demo_endpoint(request: Request, user_id: str):
    """
    Advanced demo endpoint showcasing all Redis features:
    - Response caching
    - Session management
    - Rate limiting
    - Database query caching
    - Data structures
    """
    start_time = time.time()

    # Test rate limiting
    allowed, rate_info = await rate_limiter.check_sliding_window(
        f"user:{user_id}", 10, 60
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {rate_info}",
            headers={"X-RateLimit-Reset": str(rate_info.get('reset_in', 60))}
        )

    # Get or create session
    session_data = await session_cluster.get_user_session(user_id)
    if not session_data:
        session_data = await session_cluster.create_session(user_id, {
            "login_time": time.time(),
            "preferences": {"theme": "dark"}
        })

    # Simulate database queries with caching
    user_profile = await db_cache_manager.cached_postgres_query(
        "SELECT * FROM users WHERE id = $1",
        {"user_id": user_id},
        ttl=600,
        table_dependencies=["users"]
    )

    user_preferences = await db_cache_manager.cached_mongodb_query(
        "user_preferences",
        {"user_id": user_id},
        ttl=300
    )

    # Demonstrate data structures
    leaderboard_key = "user_scores"
    await redis_ds.sorted_set_add(leaderboard_key, {"user_id": user_id, "score": 100}, 100)

    top_scores = await redis_ds.sorted_set_get_range(leaderboard_key, 0, 9)

    # Demonstrate sets for tags
    tags_key = f"user_tags:{user_id}"
    await redis_ds.set_add(tags_key, "premium", "active", "verified")

    user_tags = await redis_ds.set_members(tags_key)

    processing_time = time.time() - start_time

    return {
        "user_id": user_id,
        "profile": user_profile,
        "preferences": user_preferences,
        "session_info": session_data,
        "rate_limit_info": rate_info,
        "leaderboard_position": top_scores,
        "user_tags": list(user_tags),
        "processing_time": round(processing_time, 3),
        "redis_features_used": [
            "Response Caching",
            "Session Clustering",
            "Distributed Rate Limiting",
            "Database Query Caching",
            "Sorted Sets (Leaderboard)",
            "Sets (Tags)"
        ]
    }

# Health check endpoint
@router.get("/health")
async def redis_health_check():
    """Complete Redis health check"""
    try:
        # Test Redis connection
        redis_connected = await redis_client.test_redis_connection()

        # Get all stats
        cache_stats = api_cache_manager.get_cache_stats()
        session_stats = await session_cluster.get_session_stats()
        db_cache_stats = await db_cache_manager.get_cache_performance()
        rate_limit_stats = rate_limiter.get_rate_limit_stats()

        return {
            "redis_connected": redis_connected,
            "cache_stats": cache_stats,
            "session_cluster": session_stats,
            "database_cache": db_cache_stats,
            "rate_limiting": rate_limit_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e), "redis_connected": False}
