import asyncio
from datetime import datetime

from database import get_pool


async def auto_delete_worker():
    while True:
        try:
            pool = await get_pool()

            now = datetime.now()

            rows = await pool.fetch(
                """
                SELECT code
                FROM files
                WHERE expires_at IS NOT NULL
                  AND expires_at < $1
                """,
                now
            )

            for row in rows:
                code = row["code"]

                await pool.execute(
                    "DELETE FROM files WHERE code=$1",
                    code
                )

                print(f"🗑 Deleted expired file: {code}")

        except Exception as e:
            print("AUTO DELETE ERROR:", e)

        await asyncio.sleep(60)
