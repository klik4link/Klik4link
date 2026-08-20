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
                    callback_data=f"approve_pay:{user_id}:{code}",
                ),
                InlineKeyboardButton(
                    text="❌ Tolak",
                    callback_data=f"reject_pay:{user_id}:{code}",
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

    try:
        _, user_id_raw, code = call.data.split(":", 2)
        user_id = int(user_id_raw)
    except (ValueError, AttributeError):
        return await call.answer(
            "Data pembayaran tidak valid.",
            show_alert=True,
        )

    # =================================================
    # Ambil pembayaran TERBARU
    # Tidak menggunakan kolom id
    # =================================================

    purchase = await fetchrow(
        """
        SELECT
            user_id,
            file_code,
            owner_id,
            paid_price,
            invoice_id,
            payment_id,
            status,
            qr_message_id,
            qr_chat_id,
            created_at,
            paid_at
        FROM file_purchases
        WHERE user_id = $1
          AND file_code = $2
        ORDER BY created_at DESC NULLS LAST
        LIMIT 1
        """,
        user_id,
        code,
    )

    if not purchase:
        return await call.answer(
            "Data pembayaran tidak ditemukan.",
            show_alert=True,
        )

    status = (purchase["status"] or "").lower()

    if status == "paid":
        return await call.answer(
            "Pembayaran sudah disetujui.",
            show_alert=True,
        )

    if status in {"rejected", "cancelled", "failed"}:
        return await call.answer(
            "Pembayaran sudah ditolak/gagal.",
            show_alert=True,
        )

    # =================================================
    # UPDATE PEMBAYARAN
    # Tidak menggunakan WHERE id
    # =================================================

    updated = await execute(
        """
        UPDATE file_purchases
        SET
            status = 'paid',
            paid_at = NOW(),
            updated_at = NOW()
        WHERE user_id = $1
          AND file_code = $2
          AND status NOT IN ('paid', 'rejected', 'cancelled', 'failed')
          AND created_at = $3
        """,
        user_id,
        code,
        purchase["created_at"],
    )

    # Pastikan benar-benar ada row yang di-update
    if not updated or not str(updated).startswith("UPDATE 1"):
        # Bisa saja sudah diproses oleh worker/admin lain
        latest = await fetchrow(
            """
            SELECT status
            FROM file_purchases
            WHERE user_id = $1
              AND file_code = $2
            ORDER BY created_at DESC NULLS LAST
            LIMIT 1
            """,
            user_id,
            code,
        )

        if latest and latest["status"] == "paid":
            return await call.answer(
                "Pembayaran sudah diproses.",
                show_alert=True,
            )

        return await call.answer(
            "Pembayaran gagal diproses.",
            show_alert=True,
        )

    # =================================================
    # NOTIF KE PEMBELI
    # =================================================

    try:
        await call.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ <b>Pembayaran Berhasil Disetujui</b>\n\n"
                f"📂 File : <code>{code}</code>\n\n"
                "Sekarang kirim kembali kode file tersebut untuk membukanya."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # =================================================
    # LOG KE CHANNEL
    # =================================================

    try:
        paid_price = purchase["paid_price"] or 0

        await call.bot.send_message(
            CHANNEL_ID,
            (
                "💳 <b>PEMBAYARAN BERHASIL</b>\n\n"
                f"👤 User : <code>{user_id}</code>\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {paid_price:,}\n"
                f"👮 Admin : <code>{call.from_user.id}</code>\n\n"
                "✅ Status : <b>DISETUJUI</b>"
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # =================================================
    # UPDATE TAMPILAN ADMIN
    # =================================================

    try:
        await call.message.edit_text(
            (
                "✅ <b>PEMBAYARAN DISETUJUI</b>\n\n"
                f"👤 User : <code>{user_id}</code>\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {(purchase['paid_price'] or 0):,}\n\n"
                f"👮 Admin : <code>{call.from_user.id}</code>"
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await call.answer("Pembayaran berhasil disetujui.")


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

    try:
        _, user_id_raw, code = call.data.split(":", 2)
        user_id = int(user_id_raw)
    except (ValueError, AttributeError):
        return await call.answer(
            "Data pembayaran tidak valid.",
            show_alert=True,
        )

    # =================================================
    # Ambil pembayaran TERBARU
    # =================================================

    purchase = await fetchrow(
        """
        SELECT
            user_id,
            file_code,
            owner_id,
            paid_price,
            invoice_id,
            payment_id,
            status,
            qr_message_id,
            qr_chat_id,
            created_at,
            paid_at
        FROM file_purchases
        WHERE user_id = $1
          AND file_code = $2
        ORDER BY created_at DESC NULLS LAST
        LIMIT 1
        """,
        user_id,
        code,
    )

    if not purchase:
        return await call.answer(
            "Data pembayaran tidak ditemukan.",
            show_alert=True,
        )

    status = (purchase["status"] or "").lower()

    if status == "paid":
        return await call.answer(
            "Pembayaran sudah disetujui, tidak bisa ditolak.",
            show_alert=True,
        )

    if status in {"rejected", "cancelled", "failed"}:
        return await call.answer(
            "Pembayaran sudah ditolak/gagal.",
            show_alert=True,
        )

    # =================================================
    # UPDATE REJECT
    # =================================================

    updated = await execute(
        """
        UPDATE file_purchases
        SET
            status = 'rejected',
            updated_at = NOW()
        WHERE user_id = $1
          AND file_code = $2
          AND status NOT IN ('paid', 'rejected', 'cancelled', 'failed')
          AND created_at = $3
        """,
        user_id,
        code,
        purchase["created_at"],
    )

    if not updated or not str(updated).startswith("UPDATE 1"):
        return await call.answer(
            "Pembayaran sudah diproses atau gagal diproses.",
            show_alert=True,
        )

    # =================================================
    # NOTIF KE PEMBELI
    # =================================================

    try:
        await call.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ <b>Pembayaran Ditolak</b>\n\n"
                f"📂 File : <code>{code}</code>\n\n"
                "Silakan hubungi admin apabila merasa sudah melakukan pembayaran."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # =================================================
    # LOG KE CHANNEL
    # =================================================

    try:
        paid_price = purchase["paid_price"] or 0

        await call.bot.send_message(
            CHANNEL_ID,
            (
                "❌ <b>PEMBAYARAN DITOLAK</b>\n\n"
                f"👤 User : <code>{user_id}</code>\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {paid_price:,}\n"
                f"👮 Admin : <code>{call.from_user.id}</code>\n\n"
                "❌ Status : <b>DITOLAK</b>"
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # =================================================
    # UPDATE TAMPILAN ADMIN
    # =================================================

    try:
        await call.message.edit_text(
            (
                "❌ <b>PEMBAYARAN DITOLAK</b>\n\n"
                f"👤 User : <code>{user_id}</code>\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {(purchase['paid_price'] or 0):,}\n\n"
                f"👮 Admin : <code>{call.from_user.id}</code>"
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await call.answer("Pembayaran berhasil ditolak.")
