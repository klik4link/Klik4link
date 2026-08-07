# handlers/admin_purchase.py

import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import ADMIN_IDS
from database import get_pool


router = Router()

logger = logging.getLogger(__name__)


# =====================================
# NOTIF ADMIN PEMBELIAN
# =====================================

async def notify_admin_purchase(
    bot,
    user_id: int,
    code: str,
    price: int
):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ TERIMA",
                    callback_data=f"approve_purchase:{user_id}:{code}"
                ),
                InlineKeyboardButton(
                    text="❌ TOLAK",
                    callback_data=f"reject_purchase:{user_id}:{code}"
                )
            ]
        ]
    )


    text = (
        "🛒 <b>PEMBELIAN BARU</b>\n\n"
        "━━━━━━━━━━━━━━\n"
        f"👤 User ID : <code>{user_id}</code>\n"
        f"📂 Code : <code>{code}</code>\n"
        f"💰 Harga : Rp {price:,}\n"
        "━━━━━━━━━━━━━━\n\n"
        "Menunggu konfirmasi admin."
    ).replace(",", ".")


    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

        except Exception:
            logger.exception(
                "Gagal kirim notif admin"
            )


# =====================================
# APPROVE PURCHASE
# =====================================

@router.callback_query(
    F.data.startswith("approve_purchase:")
)
async def approve_purchase(
    callback: CallbackQuery
):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(
            "Tidak memiliki akses",
            show_alert=True
        )
        return


    _, user_id, code = callback.data.split(":")

    user_id = int(user_id)

    pool = await get_pool()


    purchase = await pool.fetchrow(
        """
        SELECT *
        FROM file_purchases
        WHERE user_id=$1
        AND file_code=$2
        """,
        user_id,
        code
    )


    if not purchase:

        await callback.answer(
            "Pembelian tidak ditemukan",
            show_alert=True
        )
        return


    if purchase["status"] == "paid":

        await callback.answer(
            "Sudah dibayar",
            show_alert=True
        )
        return



    await pool.execute(
        """
        UPDATE file_purchases
        SET
            status='paid',
            paid_at=NOW()
        WHERE user_id=$1
        AND file_code=$2
        AND status='pending'
        """,
        user_id,
        code
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 BUKA FILE",
                    callback_data=f"open_file:{code}"
                )
            ]
        ]
    )


    await callback.message.edit_text(
        (
            "✅ <b>PEMBELIAN DITERIMA</b>\n\n"
            f"👤 User : <code>{user_id}</code>\n"
            f"📂 Code : <code>{code}</code>"
        ),
        parse_mode="HTML"
    )


    await callback.bot.send_message(
        user_id,
        (
            "🎉 <b>Pembayaran Dikonfirmasi</b>\n\n"
            f"📂 Code : <code>{code}</code>\n\n"
            "File sudah aktif."
        ),
        parse_mode="HTML",
        reply_markup=keyboard
    )


    await callback.answer(
        "Berhasil"
    )


# =====================================
# REJECT PURCHASE
# =====================================

@router.callback_query(
    F.data.startswith("reject_purchase:")
)
async def reject_purchase(
    callback: CallbackQuery
):

    if callback.from_user.id not in ADMIN_IDS:

        await callback.answer(
            "Tidak memiliki akses",
            show_alert=True
        )
        return


    _, user_id, code = callback.data.split(":")

    user_id = int(user_id)

    pool = await get_pool()


    await pool.execute(
        """
        UPDATE file_purchases
        SET status='rejected'
        WHERE user_id=$1
        AND file_code=$2
        """,
        user_id,
        code
    )


    await callback.message.edit_text(
        (
            "❌ <b>PEMBELIAN DITOLAK</b>\n\n"
            f"👤 User : <code>{user_id}</code>\n"
            f"📂 Code : <code>{code}</code>"
        ),
        parse_mode="HTML"
    )


    await callback.bot.send_message(
        user_id,
        (
            "❌ <b>Pembayaran Ditolak</b>\n\n"
            f"📂 Code : <code>{code}</code>\n\n"
            "Silakan hubungi admin."
        ),
        parse_mode="HTML"
    )


    await callback.answer(
        "Ditolak"
    )
