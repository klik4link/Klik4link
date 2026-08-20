import asyncio
import logging

import asyncpg

from config import DATABASE_URL

_pool = None
_lock = asyncio.Lock()

# Supabase/PgBouncer friendly and conservative for small projects.
POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 5
POOL_COMMAND_TIMEOUT = 60
POOL_MAX_IDLE = 300
POOL_CONNECT_TIMEOUT = 30


async def get_pool():
    """Return one shared PostgreSQL pool for the whole application."""
    global _pool

    if _pool is not None and not _pool.is_closing():
        return _pool

    async with _lock:
        if _pool is not None and not _pool.is_closing():
            return _pool

        # Do not hammer Supabase when it temporarily refuses connections.
        delay = 3
        last_error = None

        for attempt in range(1, 6):
            try:
                logging.info(
                    "🔌 Connecting to PostgreSQL (attempt %s/5)...",
                    attempt,
                )

                new_pool = await asyncpg.create_pool(
                    dsn=DATABASE_URL,
                    min_size=POOL_MIN_SIZE,
                    max_size=POOL_MAX_SIZE,
                    command_timeout=POOL_COMMAND_TIMEOUT,
                    max_inactive_connection_lifetime=POOL_MAX_IDLE,
                    timeout=POOL_CONNECT_TIMEOUT,
                    statement_cache_size=0,
                )

                _pool = new_pool
                logging.info(
                    "✅ PostgreSQL connected | pool=%s-%s",
                    POOL_MIN_SIZE,
                    POOL_MAX_SIZE,
                )
                return _pool

            except Exception as exc:
                last_error = exc
                logging.exception("❌ PostgreSQL connection failed")

                if attempt < 5:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 30)

        raise RuntimeError(
            "PostgreSQL connection failed after 5 attempts. "
            "Check DATABASE_URL and Supabase compute/connection limits."
        ) from last_error


async def close_db():
    global _pool

    async with _lock:
        if _pool is not None:
            try:
                await _pool.close()
            finally:
                _pool = None
                logging.info("🔌 Database closed")


async def execute(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.execute(query, *args)
        except (asyncpg.PostgresConnectionError, asyncio.TimeoutError):
            logging.exception("EXECUTE CONNECTION ERROR")
            await close_db()
            if attempt >= retry:
                raise
            await asyncio.sleep(1)
        except Exception:
            logging.exception("EXECUTE ERROR")
            if attempt >= retry:
                raise
            await asyncio.sleep(1)


async def fetch(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetch(query, *args)
        except (asyncpg.PostgresConnectionError, asyncio.TimeoutError):
            logging.exception("FETCH CONNECTION ERROR")
            await close_db()
            if attempt >= retry:
                raise
            await asyncio.sleep(1)
        except Exception:
            logging.exception("FETCH ERROR")
            if attempt >= retry:
                raise
            await asyncio.sleep(1)


async def fetchrow(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetchrow(query, *args)
        except (asyncpg.PostgresConnectionError, asyncio.TimeoutError):
            logging.exception("FETCHROW CONNECTION ERROR")
            await close_db()
            if attempt >= retry:
                raise
            await asyncio.sleep(1)
        except Exception:
            logging.exception("FETCHROW ERROR")
            if attempt >= retry:
                raise
            await asyncio.sleep(1)


async def fetchval(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetchval(query, *args)
        except (asyncpg.PostgresConnectionError, asyncio.TimeoutError):
            logging.exception("FETCHVAL CONNECTION ERROR")
            await close_db()
            if attempt >= retry:
                raise
            await asyncio.sleep(1)
        except Exception:
            logging.exception("FETCHVAL ERROR")
            if attempt >= retry:
                raise
            await asyncio.sleep(1)


async def transaction(queries: list):
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            results = []
            for q in queries:
                query = q[0]
                args = q[1:]
                results.append(await conn.execute(query, *args))
            return results
