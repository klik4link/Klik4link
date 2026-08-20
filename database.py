import asyncio
import logging

import asyncpg

from config import DATABASE_URL

_pool = None
_lock = asyncio.Lock()

POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 5
POOL_COMMAND_TIMEOUT = 60
POOL_MAX_IDLE = 300
POOL_CONNECT_TIMEOUT = 30


async def get_pool():
    global _pool

    if _pool is not None and not _pool.is_closing():
        return _pool

    async with _lock:
        if _pool is not None and not _pool.is_closing():
            return _pool

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

            except asyncpg.InsufficientResourcesError as exc:
                logging.error(
                    "❌ PostgreSQL compute/connection quota exceeded: %s",
                    exc,
                )
                raise

            except (
                asyncpg.InvalidPasswordError,
                asyncpg.InvalidAuthorizationSpecificationError,
            ) as exc:
                logging.error(
                    "❌ PostgreSQL authentication failed: %s",
                    exc,
                )
                raise

            except Exception as exc:
                last_error = exc

                logging.exception(
                    "❌ PostgreSQL connection failed"
                )

                if attempt < 5:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 30)

        raise RuntimeError(
            "PostgreSQL connection failed after 5 attempts. "
            "Check DATABASE_URL, Supabase status, and connection limits."
        ) from last_error


async def close_db():
    global _pool

    async with _lock:
        if _pool is not None:
            try:
                await _pool.close()
            except Exception:
                logging.exception("❌ Error closing PostgreSQL pool")
            finally:
                _pool = None
                logging.info("🔌 Database closed")


def _is_retryable(exc):
    return isinstance(
        exc,
        (
            asyncpg.PostgresConnectionError,
            asyncio.TimeoutError,
        ),
    )


async def execute(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.execute(query, *args)

        except Exception as exc:
            if not _is_retryable(exc):
                logging.exception("EXECUTE ERROR")
                raise

            logging.warning(
                "⚠️ EXECUTE connection error "
                "(attempt %s/%s)",
                attempt + 1,
                retry + 1,
            )

            await close_db()

            if attempt >= retry:
                raise

            await asyncio.sleep(1)


async def fetch(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetch(query, *args)

        except Exception as exc:
            if not _is_retryable(exc):
                logging.exception("FETCH ERROR")
                raise

            logging.warning(
                "⚠️ FETCH connection error "
                "(attempt %s/%s)",
                attempt + 1,
                retry + 1,
            )

            await close_db()

            if attempt >= retry:
                raise

            await asyncio.sleep(1)


async def fetchrow(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetchrow(query, *args)

        except Exception as exc:
            if not _is_retryable(exc):
                logging.exception("FETCHROW ERROR")
                raise

            logging.warning(
                "⚠️ FETCHROW connection error "
                "(attempt %s/%s)",
                attempt + 1,
                retry + 1,
            )

            await close_db()

            if attempt >= retry:
                raise

            await asyncio.sleep(1)


async def fetchval(query, *args, retry=1):
    for attempt in range(retry + 1):
        try:
            pool = await get_pool()
            return await pool.fetchval(query, *args)

        except Exception as exc:
            if not _is_retryable(exc):
                logging.exception("FETCHVAL ERROR")
                raise

            logging.warning(
                "⚠️ FETCHVAL connection error "
                "(attempt %s/%s)",
                attempt + 1,
                retry + 1,
            )

            await close_db()

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

                results.append(
                    await conn.execute(query, *args)
                )

            return results
