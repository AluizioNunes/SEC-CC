import os
import asyncpg

_pool = None


def normalize_dsn(dsn: str) -> str:
    if "+asyncpg" in dsn:
        return dsn.replace("+asyncpg", "")
    return dsn


def build_dsn_from_env() -> str | None:
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    if all([host, port, user, password, db]):
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return None


async def init_pool():
    global _pool
    if _pool is None:
        # Prefer explicit POSTGRES_* envs, fallback to DATABASE_URL, then default
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            dsn = build_dsn_from_env() or "postgresql://sec:secpass2024@postgres:5432/secdb"
        dsn = normalize_dsn(dsn)
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10)
    return _pool


async def get_pool():
    global _pool
    if _pool is None:
        await init_pool()
    return _pool