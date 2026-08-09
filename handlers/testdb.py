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
            WHERE table_schema='public'
            AND table_name='file_purchases'
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
        # =========================
        # CEK USERS
        # =========================
        check_users = await pool.fetch(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema='public'
            AND table_name='users'
            ORDER BY ordinal_position
            """
        )
        text += "\n👤 <b>USERS:</b>\n"
        if check_users:
            for col in check_users:
                text += (
                    f"• {col['column_name']} "
                    f"({col['data_type']})\n"
                )
        else:
            text += "❌ Tabel users tidak ada\n"
        # =========================
        # CEK KOLOM VIP
        # =========================
        vip_columns = await pool.fetch(
            """
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema='public'
            AND table_name='users'
            AND (
                LOWER(column_name) LIKE '%vip%'
                OR LOWER(column_name) LIKE '%premium%'
            )
            ORDER BY ordinal_position
            """
        )
        text += "\n💎 <b>VIP / PREMIUM COLUMNS:</b>\n"
        if vip_columns:
            for col in vip_columns:
                text += (
                    f"• <code>{col['column_name']}</code> "
                    f"({col['data_type']})\n"
                )
        else:
            text += (
                "❌ Tidak ditemukan kolom VIP/Premium "
                "di tabel users.\n"
            )
        # =========================
        # CEK USER SAAT INI
        # =========================
        user = await pool.fetchrow(
            """
            SELECT *
            FROM users
            WHERE telegram_id=$1
            """,
            message.from_user.id
        )
        text += "\n🔎 <b>USER SAAT INI:</b>\n"
        if user:
            text += (
                f"🆔 Telegram ID : "
                f"<code>{message.from_user.id}</code>\n"
            )
            # tampilkan hanya kolom yang berhubungan
            # dengan VIP / Premium
            found_vip_value = False
            for key in user.keys():
                key_lower = key.lower()
                if (
                    "vip" in key_lower
                    or "premium" in key_lower
                ):
                    text += (
                        f"💎 {key} : "
                        f"<code>{user[key]}</code>\n"
                    )
                    found_vip_value = True
            if not found_vip_value:
                text += (
                    "❌ User tidak memiliki "
                    "kolom VIP/Premium.\n"
                )
        else:
            text += (
                "❌ User belum ditemukan "
                "di tabel users.\n"
            )
        # =========================
        # SEND RESULT
        # =========================
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
