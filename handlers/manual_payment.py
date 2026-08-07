import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import fetchrow, execute
from config import ADMIN_IDS


router = Router()

logger = logging.getLogger(__name__)


# =================================================
# USER KLIK SUDAH BAYAR
# =================================================

@router.callback_query(
    F.data.startswith("manual_check:")
)
async def manual_check(call: CallbackQuery):

    invoice_id = call.data.split(":")[1]


    purchase = await fetchrow(
        """
        SELECT
            *
        FROM file_purchases
        WHERE invoice_id=$1
        """,
        invoice_id
    )


    if not purchase:

        return await call.answer(
            "Pembayaran tidak ditemukan",
            show_alert=True
        )


    if purchase["status"] == "paid":

        return await call.answer(
            "Sudah dibayar",
            show_alert=True
        )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✅ SETUJUI",
                    callback_data=f"approve_manual:{invoice_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ TOLAK",
                    callback_data=f"reject_manual:{invoice_id}"
                )
            ]

        ]
    )


    text = (
        "🔔 <b>REQUEST PEMBAYARAN MANUAL</b>\n\n"
        f"👤 User ID : <code>{purchase['user_id']}</code>\n"
        f"📂 File : <code>{purchase['file_code']}</code>\n"
        f"💰 Nominal : Rp {purchase['paid_price']:,}\n"
        f"🧾 Invoice : <code>{invoice_id}</code>"
    ).replace(",", ".")


    for admin in ADMIN_IDS:

        try:

            await call.bot.send_message(
                admin,
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

        except Exception as e:

            logger.error(e)



    await call.answer(
        "Menunggu konfirmasi admin"
    )



# =================================================
# ADMIN SETUJUI
# =================================================

@router.callback_query(
    F.data.startswith("approve_manual:")
)
async def approve_manual(call: CallbackQuery):


    if call.from_user.id not in ADMIN_IDS:

        return await call.answer(
            "Tidak memiliki akses",
            show_alert=True
        )



    invoice_id = call.data.split(":")[1]



    purchase = await fetchrow(
        """
        SELECT *
        FROM file_purchases
        WHERE invoice_id=$1
        """,
        invoice_id
    )



    if not purchase:

        return await call.answer(
            "Data tidak ditemukan",
            show_alert=True
        )



    await execute(
        """
        UPDATE file_purchases
        SET status='paid'
        WHERE invoice_id=$1
        """,
        invoice_id
    )



    await call.bot.send_message(
        purchase["user_id"],
        (
            "✅ <b>Pembayaran Disetujui</b>\n\n"
            f"📂 Code File:\n"
            f"<code>{purchase['file_code']}</code>\n\n"
            "Silakan buka menu Get File."
        ),
        parse_mode="HTML"
    )



    await call.message.edit_text(
        "✅ Pembayaran manual disetujui\n\n"
        f"File: {purchase['file_code']}"
    )



# =================================================
# ADMIN TOLAK
# =================================================

@router.callback_query(
    F.data.startswith("reject_manual:")
)
async def reject_manual(call: CallbackQuery):


    if call.from_user.id not in ADMIN_IDS:

        return await call.answer(
            "Tidak memiliki akses",
            show_alert=True
        )



    invoice_id = call.data.split(":")[1]


    purchase = await fetchrow(
        """
        SELECT *
        FROM file_purchases
        WHERE invoice_id=$1
        """,
        invoice_id
    )



    if purchase:

        await execute(
            """
            UPDATE file_purchases
            SET status='cancelled'
            WHERE invoice_id=$1
            """,
            invoice_id
        )



        await call.bot.send_message(
            purchase["user_id"],
            "❌ Pembayaran ditolak admin."
        )



    await call.message.edit_text(
        "❌ Pembayaran manual ditolak."
    )
