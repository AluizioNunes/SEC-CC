import os
import time
import re
import asyncpg
from .monitoring import metrics_collector

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


def _extract_query_info(sql: str) -> tuple[str, str | None]:
    s = sql.strip()
    sl = s.lower()
    if sl.startswith("select"):
        qtype = "select"
    elif sl.startswith("insert"):
        qtype = "insert"
    elif sl.startswith("update"):
        qtype = "update"
    elif sl.startswith("delete"):
        qtype = "delete"
    else:
        qtype = "other"

    tbl = None
    m = re.search(r'from\s+"?([A-Za-z0-9_]+)"?\."?([A-Za-z0-9_]+)"?', s, flags=re.IGNORECASE)
    if not m:
        m = re.search(r'insert\s+into\s+"?([A-Za-z0-9_]+)"?\."?([A-Za-z0-9_]+)"?', s, flags=re.IGNORECASE)
    if not m:
        m = re.search(r'update\s+"?([A-Za-z0-9_]+)"?\."?([A-Za-z0-9_]+)"?', s, flags=re.IGNORECASE)
    if not m:
        m = re.search(r'delete\s+from\s+"?([A-Za-z0-9_]+)"?\."?([A-Za-z0-9_]+)"?', s, flags=re.IGNORECASE)
    if m:
        tbl = f"{m.group(1)}.{m.group(2)}"
    return qtype, tbl


async def instrumented_fetch(sql: str, *args, pool: asyncpg.Pool | None = None, query_type: str | None = None, table: str | None = None):
    if pool is None:
        pool = await get_pool()
    start = time.time()
    try:
        result = await pool.fetch(sql, *args)
        return result
    finally:
        elapsed = time.time() - start
        qt, tbl = _extract_query_info(sql)
        metrics_collector.record_database_query(query_type or qt, table or (tbl or "unknown"), elapsed)


async def instrumented_fetchrow(sql: str, *args, pool: asyncpg.Pool | None = None, query_type: str | None = None, table: str | None = None):
    if pool is None:
        pool = await get_pool()
    start = time.time()
    try:
        result = await pool.fetchrow(sql, *args)
        return result
    finally:
        elapsed = time.time() - start
        qt, tbl = _extract_query_info(sql)
        metrics_collector.record_database_query(query_type or qt, table or (tbl or "unknown"), elapsed)


async def instrumented_fetchval(sql: str, *args, pool: asyncpg.Pool | None = None, query_type: str | None = None, table: str | None = None):
    if pool is None:
        pool = await get_pool()
    start = time.time()
    try:
        result = await pool.fetchval(sql, *args)
        return result
    finally:
        elapsed = time.time() - start
        qt, tbl = _extract_query_info(sql)
        metrics_collector.record_database_query(query_type or qt, table or (tbl or "unknown"), elapsed)


async def instrumented_execute(sql: str, *args, pool: asyncpg.Pool | None = None, query_type: str | None = None, table: str | None = None):
    if pool is None:
        pool = await get_pool()
    start = time.time()
    try:
        result = await pool.execute(sql, *args)
        return result
    finally:
        elapsed = time.time() - start
        qt, tbl = _extract_query_info(sql)
        metrics_collector.record_database_query(query_type or qt, table or (tbl or "unknown"), elapsed)