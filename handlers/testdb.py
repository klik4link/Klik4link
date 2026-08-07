from aiogram import Router, F
from aiogram.types import Message

from database import get_pool


router = Router()


# =================================================
# TEST DATABASE CONNECTION
# =================================================

@router.message(F.text == "/testdb")
async def test_db(message: Message):

    try:

        pool = await get_pool()


        # =========================
        # CEK DATABASE
        # =========================

        db_name = await pool.fetchval(
            "SELECT current_database();"
        )


        # =========================
        # CEK TABLE
        # =========================

        tables = await pool.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            ORDER BY table_name
            """
        )


        text = (
            "✅ <b>DATABASE CONNECT</b>\n\n"
            f"🗄 Database:\n"
            f"<code>{db_name}</code>\n\n"
            "📂 TABLE:\n"
        )


        if tables:

            for row in tables:

                text += (
                    f"• <code>{row['table_name']}</code>\n"
                )

        else:

            text += "Tidak ada tabel.\n"



        # =========================
        # CEK FILE PURCHASE
        # =========================

        check_purchase = await pool.fetch(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name='file_purchases'
            ORDER BY ordinal_position
            """
        )


        text += "\n💳 <b>FILE_PURCHASES:</b>\n"


        if check_purchase:

            for col in check_purchase:

                text += (
                    f"• {col['column_name']} "
                    f"({col['data_type']})\n"
                )

        else:

            text += "❌ Tabel file_purchases tidak ada\n"



        await message.answer(
            text,
            parse_mode="HTML"
        )



    except Exception as e:


        await message.answer(
            "❌ <b>DATABASE ERROR</b>\n\n"
            f"<code>{e}</code>",
            parse_mode="HTML"
        )
