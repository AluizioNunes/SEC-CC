"""
Redis advanced data structures operations
"""
from typing import List, Set, Dict, Any, Optional, Union
from .client import get_redis_client

async def hash_operations() -> Dict[str, Any]:
    """Hash operations - store objects as key-value pairs"""
    redis_client = get_redis_client()

    # User profile example
    user_key = "user:123"

    # Set multiple fields
    await redis_client.hset(user_key, mapping={
        "name": "João Silva",
        "email": "joao@example.com",
        "age": "30",
        "city": "São Paulo"
    })

    # Get specific field
    name = await redis_client.hget(user_key, "name")

    # Get all fields
    user_data = await redis_client.hgetall(user_key)

    # Check if field exists
    exists = await redis_client.hexists(user_key, "email")

    # Get all field names
    fields = await redis_client.hkeys(user_key)

    # Get all values
    values = await redis_client.hvals(user_key)

    # Increment field (useful for counters)
    await redis_client.hincrby(user_key, "login_count", 1)

    return {
        "name": name,
        "user_data": user_data,
        "exists": exists,
        "fields": fields,
        "values": values,
        "login_count": await redis_client.hget(user_key, "login_count")
    }

async def set_operations() -> Dict[str, Any]:
    """Set operations - store unique items"""
    redis_client = get_redis_client()

    # Tags for articles
    article_tags = "article:tags:1"

    # Add tags
    await redis_client.sadd(article_tags, "tecnologia", "python", "redis", "fastapi")

    # Check membership
    is_tech = await redis_client.sismember(article_tags, "tecnologia")
    is_java = await redis_client.sismember(article_tags, "java")

    # Get all members
    tags = await redis_client.smembers(article_tags)

    # Get random member
    random_tag = await redis_client.srandmember(article_tags)

    # Get cardinality (size)
    size = await redis_client.scard(article_tags)

    return {
        "is_tech": is_tech,
        "is_java": is_java,
        "tags": tags,
        "random_tag": random_tag,
        "size": size
    }

async def sorted_set_operations() -> Dict[str, Any]:
    """Sorted Set operations - ordered collections with scores"""
    redis_client = get_redis_client()

    # Leaderboard example
    leaderboard = "game:leaderboard"

    # Add players with scores
    await redis_client.zadd(leaderboard, {
        "player1": 1000,
        "player2": 850,
        "player3": 1200,
        "player4": 750
    })

    # Get top players
    top_players = await redis_client.zrevrange(leaderboard, 0, 2, withscores=True)

    # Get player rank
    player_rank = await redis_client.zrevrank(leaderboard, "player1")

    # Get players in score range
    high_scorers = await redis_client.zrangebyscore(leaderboard, 800, 1500, withscores=True)

    # Increment score
    await redis_client.zincrby(leaderboard, 100, "player1")

    return {
        "top_players": top_players,
        "player_rank": player_rank,
        "high_scorers": high_scorers,
        "new_score": await redis_client.zscore(leaderboard, "player1")
    }

async def list_operations() -> Dict[str, Any]:
    """List operations - ordered collections"""
    redis_client = get_redis_client()

    # Task queue example
    task_queue = "tasks:pending"

    # Add tasks to queue
    await redis_client.lpush(task_queue, "task1", "task2", "task3")

    # Get queue length
    length = await redis_client.llen(task_queue)

    # Get all tasks
    tasks = await redis_client.lrange(task_queue, 0, -1)

    # Process task (remove from front)
    first_task = await redis_client.rpop(task_queue)

    # Add task to front (priority)
    await redis_client.lpush(task_queue, "urgent_task")

    return {
        "length": length,
        "tasks": tasks,
        "first_task": first_task,
        "new_length": await redis_client.llen(task_queue)
    }

async def get_all_data_structures() -> Dict[str, Any]:
    """Get examples of all data structures"""
    return {
        "hash_example": await hash_operations(),
        "set_example": await set_operations(),
        "sorted_set_example": await sorted_set_operations(),
        "list_example": await list_operations()
    }
