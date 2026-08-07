from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import ADMIN_IDS
from database import fetchrow, execute

router = Router()

CHANNEL_ID = -1004413314849

# =====================================================
# KIRIM NOTIF KE ADMIN
# =====================================================

async def notify_admin_purchase(
    bot,
    user_id: int,
    code: str,
    price: int,
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
                ),
            ]
        ]
    )

    text = (
        "💳 <b>PEMBAYARAN BARU</b>\n\n"
        f"👤 User : <code>{user_id}</code>\n"
        f"📂 File : <code>{code}</code>\n"
        f"💰 Nominal : Rp {price:,}\n\n"
        "Silakan cek mutasi lalu pilih tombol di bawah."
    ).replace(",", ".")

    for admin in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        except Exception:
            pass


# =====================================================
# APPROVE PEMBAYARAN
# =====================================================

@router.callback_query(
    F.data.startswith("approve_pay:")
)
async def approve_pay(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return await call.answer(
            "Tidak memiliki akses.",
            show_alert=True,
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
        code,
    )

    if not purchase:
        return await call.answer(
            "Data tidak ditemukan.",
            show_alert=True,
        )

    if purchase["status"] == "paid":
        return await call.answer(
            "Pembayaran sudah disetujui.",
            show_alert=True,
        )

    await execute(
        """
        UPDATE file_purchases
        SET
            status='paid',
            paid_at=NOW()
        WHERE id=$1
        """,
        purchase["id"],
    )

    # Kirim notifikasi ke pembeli
    try:
        await call.bot.send_message(
            int(user_id),
            (
                "✅ <b>Pembayaran Berhasil Disetujui</b>\n\n"
                f"📂 File : <code>{code}</code>\n\n"
                "Sekarang kirim kembali kode file tersebut untuk membukanya."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Kirim log ke channel
    try:
        await call.bot.send_message(
            CHANNEL_ID,
            (
                "💳 <b>PEMBAYARAN BERHASIL</b>\n\n"
                f"👤 User : <code>{user_id}</code>\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {purchase['paid_price']:,}\n"
                f"👮 Admin : <code>{call.from_user.id}</code>\n\n"
                "✅ Status : <b>DISETUJUI</b>"
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await call.message.edit_text(
        (
            "✅ <b>PEMBAYARAN DISETUJUI</b>\n\n"
            f"👤 User : <code>{user_id}</code>\n"
            f"📂 File : <code>{code}</code>\n\n"
            f"👮 Admin : <code>{call.from_user.id}</code>"
        ),
        parse_mode="HTML",
    )

    await call.answer("Berhasil disetujui.")


# =====================================================
# TOLAK PEMBAYARAN
# =====================================================

@router.callback_query(
    F.data.startswith("reject_pay:")
)
async def reject_pay(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return await call.answer(
            "Tidak memiliki akses.",
            show_alert=True,
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
        code,
    )

    if not purchase:
        return await call.answer(
            "Data tidak ditemukan.",
            show_alert=True,
        )

    if purchase["status"] == "paid":
        return await call.answer(
            "Pembayaran sudah disetujui.",
            show_alert=True,
        )

    await execute(
        """
        UPDATE file_purchases
        SET status='rejected'
        WHERE id=$1
        """,
        purchase["id"],
    )

    try:
        await call.bot.send_message(
            int(user_id),
            (
                "❌ <b>Pembayaran Ditolak</b>\n\n"
                f"📂 File : <code>{code}</code>\n\n"
                "Silakan hubungi admin apabila merasa sudah melakukan pembayaran."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await call.message.edit_text(
        (
            "❌ <b>PEMBAYARAN DITOLAK</b>\n\n"
            f"👤 User : <code>{user_id}</code>\n"
            f"📂 File : <code>{code}</code>\n\n"
            f"👮 Admin : <code>{call.from_user.id}</code>"
        ),
        parse_mode="HTML",
    )

    await call.answer("Pembayaran ditolak.")
