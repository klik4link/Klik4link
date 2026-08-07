import asyncio
from database import get_pool


async def main():

    pool = await get_pool()

    rows = await pool.fetch(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        """
    )

    print("TABLE DATABASE:")

    for row in rows:
        print(row["table_name"])


    await pool.close()


asyncio.run(main())
