from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS
from database import fetchrow, execute


router = Router()


async def notify_admin_purchase(
    bot,
    user_id,
    code,
    price
):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Setujui",
                    callback_data=f"approve_pay:{user_id}:{code}"
                ),
                InlineKeyboardButton(
                    text="❌ Tolak",
                    callback_data=f"reject_pay:{user_id}:{code}"
                )
            ]
        ]
    )


    text = (
        "💳 <b>PEMBAYARAN BARU</b>\n\n"
        f"👤 User ID : <code>{user_id}</code>\n"
        f"📂 File : <code>{code}</code>\n"
        f"💰 Nominal : Rp {price:,}\n\n"
        "Menunggu pengecekan admin."
    ).replace(",", ".")


    for admin in ADMIN_IDS:

        await bot.send_message(
            admin,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )



# =========================
# APPROVE
# =========================

@router.callback_query(
    F.data.startswith("approve_pay:")
)
async def approve_pay(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return await call.answer(
            "Tidak punya akses",
            show_alert=True
        )


    _, user_id, code = call.data.split(":")


    purchase = await fetchrow(
        """
        SELECT *
        FROM file_purchases
        WHERE user_id=$1
        AND file_code=$2
        ORDER BY id DESC
        LIMIT 1
        """,
        int(user_id),
        code
    )


    if not purchase:
        return await call.answer(
            "Data tidak ditemukan",
            show_alert=True
        )


    await execute(
        """
        UPDATE file_purchases
        SET
            status='paid',
            paid_at=NOW()
        WHERE id=$1
        """,
        purchase["id"]
    )


    await call.bot.send_message(
        int(user_id),
        (
            "✅ <b>Pembayaran Disetujui</b>\n\n"
            f"📂 File : <code>{code}</code>\n\n"
            "Silakan kirim kembali kode file untuk membuka."
        ),
        parse_mode="HTML"
    )


    await call.message.edit_text(
        "✅ PEMBAYARAN DISETUJUI\n\n"
        f"User: {user_id}\n"
        f"File: {code}"
    )


    await call.answer()



# =========================
# REJECT
# =========================

@router.callback_query(
    F.data.startswith("reject_pay:")
)
async def reject_pay(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return await call.answer(
            "Tidak punya akses",
            show_alert=True
        )


    _, user_id, code = call.data.split(":")


    await execute(
        """
        UPDATE file_purchases
        SET status='rejected'
        WHERE user_id=$1
        AND file_code=$2
        """,
        int(user_id),
        code
    )


    await call.bot.send_message(
        int(user_id),
        (
            "❌ <b>Pembayaran Ditolak</b>\n\n"
            f"File: <code>{code}</code>\n\n"
            "Silakan hubungi admin."
        ),
        parse_mode="HTML"
    )


    await call.message.edit_text(
        "❌ PEMBAYARAN DITOLAK"
    )


    await call.answer()
