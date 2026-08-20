import asyncio
import logging
import time

from database import get_pool


logger = logging.getLogger(__name__)

# Cek setiap 60 detik
CHECK_INTERVAL = 60


async def auto_delete_worker():
    """
    Worker untuk menghapus file yang sudah expired.

    files.expires_at disimpan sebagai Unix timestamp BIGINT,
    jadi perbandingan harus menggunakan int(time.time()).
    """

    logger.info("🗑 AUTO_DELETE worker running...")

    while True:
        try:
            pool = await get_pool()

            # expires_at = BIGINT / Unix timestamp
            now = int(time.time())

            rows = await pool.fetch(
                """
                SELECT code
                FROM files
                WHERE expires_at IS NOT NULL
                  AND expires_at > 0
                  AND expires_at < $1
                """,
                now,
            )

            if rows:
                logger.info(
                    "🗑 Found %s expired file(s)",
                    len(rows),
                )

            for row in rows:
                code = row["code"]

                try:
                    result = await pool.execute(
                        """
                        DELETE FROM files
                        WHERE code = $1
                        """,
                        code,
                    )

                    logger.info(
                        "🗑 Deleted expired file: %s | %s",
                        code,
                        result,
                    )

                except Exception:
                    logger.exception(
                        "❌ Failed deleting expired file: %s",
                        code,
                    )

        except asyncio.CancelledError:
            logger.info("🛑 AUTO_DELETE worker stopped")
            raise

        except Exception:
            logger.exception("❌ AUTO DELETE ERROR")

        await asyncio.sleep(CHECK_INTERVAL)
