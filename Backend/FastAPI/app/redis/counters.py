"""
Redis advanced counters and statistics
"""
from typing import Dict, List, Tuple, Any
from .client import get_redis_client

async def increment_counter(counter_name: str, increment: int = 1) -> int:
    """Increment counter and return new value"""
    redis_client = get_redis_client()
    try:
        new_value = await redis_client.incrby(counter_name, increment)
        return new_value
    except Exception as e:
        print(f"Redis counter increment error: {e}")
        return 0

async def decrement_counter(counter_name: str, decrement: int = 1) -> int:
    """Decrement counter and return new value"""
    redis_client = get_redis_client()
    try:
        new_value = await redis_client.decrby(counter_name, decrement)
        return new_value
    except Exception as e:
        print(f"Redis counter decrement error: {e}")
        return 0

async def get_counter_value(counter_name: str) -> int:
    """Get current counter value"""
    redis_client = get_redis_client()
    try:
        value = await redis_client.get(counter_name)
        return int(value) if value else 0
    except Exception as e:
        print(f"Redis get counter error: {e}")
        return 0

async def set_counter_value(counter_name: str, value: int) -> bool:
    """Set counter to specific value"""
    redis_client = get_redis_client()
    try:
        await redis_client.set(counter_name, str(value))
        return True
    except Exception as e:
        print(f"Redis set counter error: {e}")
        return False

async def create_ranking_leaderboard() -> Dict[str, Any]:
    """Create and manage ranking leaderboard"""
    redis_client = get_redis_client()

    # Game scores example
    leaderboard = "game:scores"

    # Add players with scores
    await redis_client.zadd(leaderboard, {
        "Alice": 1500,
        "Bob": 1200,
        "Charlie": 1800,
        "Diana": 900
    })

    # Get top 3 players
    top_3 = await redis_client.zrevrange(leaderboard, 0, 2, withscores=True)

    # Add points to player
    await redis_client.zincrby(leaderboard, 200, "Bob")

    # Get updated top players
    updated_top = await redis_client.zrevrange(leaderboard, 0, 2, withscores=True)

    # Get player rank
    bob_rank = await redis_client.zrevrank(leaderboard, "Bob")

    return {
        "top_3": top_3,
        "updated_top": updated_top,
        "bob_rank": bob_rank,
        "bob_new_score": await redis_client.zscore(leaderboard, "Bob")
    }

async def create_statistics_counters() -> Dict[str, Any]:
    """Create various statistics counters"""
    redis_client = get_redis_client()

    # Page views counter
    await increment_counter("page:views:home")
    await increment_counter("page:views:about")
    await increment_counter("page:views:contact")

    # User actions counter
    await increment_counter("user:registrations")
    await increment_counter("user:logins")
    await increment_counter("user:logouts")

    # API calls counter
    await increment_counter("api:calls:fastapi")
    await increment_counter("api:calls:nestjs")

    # Get all statistics
    stats = {
        "page_views": {
            "home": await get_counter_value("page:views:home"),
            "about": await get_counter_value("page:views:about"),
            "contact": await get_counter_value("page:views:contact")
        },
        "user_actions": {
            "registrations": await get_counter_value("user:registrations"),
            "logins": await get_counter_value("user:logins"),
            "logouts": await get_counter_value("user:logouts")
        },
        "api_calls": {
            "fastapi": await get_counter_value("api:calls:fastapi"),
            "nestjs": await get_counter_value("api:calls:nestjs")
        }
    }

    return stats

async def create_activity_feed() -> List[str]:
    """Create activity feed using Redis lists"""
    redis_client = get_redis_client()

    feed_key = "activity:feed"

    # Add activities (most recent first)
    activities = [
        "User João logged in",
        "User Maria registered",
        "Product XYZ was updated",
        "Order #123 was placed",
        "Payment for order #123 confirmed"
    ]

    for activity in activities:
        await redis_client.lpush(feed_key, activity)

    # Keep only last 10 activities
    await redis_client.ltrim(feed_key, 0, 9)

    # Get recent activities
    recent_activities = await redis_client.lrange(feed_key, 0, -1)

    return recent_activities

async def get_all_counters() -> Dict[str, Any]:
    """Get examples of all counter functionalities"""
    return {
        "ranking_leaderboard": await create_ranking_leaderboard(),
        "statistics_counters": await create_statistics_counters(),
        "activity_feed": await create_activity_feed()
    }
