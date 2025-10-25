import os
import asyncpg

_pool = None


def normalize_dsn(dsn: str) -> str:
    if "+asyncpg" in dsn:
        return dsn.replace("+asyncpg", "")
    return dsn

async def init_pool():
    global _pool
    if _pool is None:
        dsn = normalize_dsn(os.getenv("DATABASE_URL", "postgresql://sec:secpass2024@postgres:5432/secdb"))
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10)
    return _pool

async def get_pool():
    global _pool
    if _pool is None:
        await init_pool()
    return _pool