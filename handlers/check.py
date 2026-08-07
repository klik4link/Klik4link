from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging

from database import fetchrow, execute
from handlers.page import send_page
from utils.bayargg import BayarGG

logger = logging.getLogger(__name__)

router = Router()

status_map = {
    "pending": "⏳ Menunggu pembayaran",
    "expired": "❌ Kadaluarsa"
}


@router.callback_query(F.data.startswith("check:"))
async def check_payment(call: CallbackQuery):
    invoice_id = call.data.split(":")[1]

    try:
        logger.info(
            "Check payment | invoice=%s | user=%s",
            invoice_id,
            call.from_user.id
        )

        # =========================
        # CEK PAYMENT GATEWAY
        # =========================
        try:
            data = await BayarGG.check_payment(invoice_id)
        except Exception:
            return await call.answer(
                "❌ Error gateway",
                show_alert=True
            )

        if not data:
            return await call.answer(
                "❌ Gagal cek payment",
                show_alert=True
            )

        status = str(
            data.get("status")
            or data.get("payment_status")
            or ""
        ).lower()

        logger.info("BAYARGG CHECK RESPONSE | %s", data)

        # =========================
        # AMBIL TRANSAKSI
        # =========================
        tx = await fetchrow(
            """
            SELECT
                user_id,
                owner_id,
                paid_price,
                file_code,
                status,
                qr_message_id,
                qr_chat_id
            FROM file_purchases
            WHERE invoice_id=$1
            """,
            invoice_id
        )

        if not tx:
            return await call.answer(
                "❌ Invoice tidak ditemukan",
                show_alert=True
            )

        # =========================
        # SUDAH DIPROSES
        # =========================
        if tx["status"] == "paid":

            await send_page(
                bot=call.bot,
                chat_id=call.message.chat.id,
                user_id=tx["user_id"],
                code=tx["file_code"],
                page=1
            )

            try:
                await call.message.delete()
            except Exception:
                pass

            return await call.answer(
                "✅ File berhasil dikirim"
            )

        # =========================
        # BELUM BAYAR
        # =========================
        if status not in ("paid", "success"):
            return await call.answer(
                status_map.get(status, "⏳ Menunggu pembayaran"),
                show_alert=True
            )

        # =========================
        # UPDATE DATABASE
        # =========================
        updated = await execute(
            """
            UPDATE file_purchases
            SET
                status='paid',
                paid_at=NOW()
            WHERE invoice_id=$1
              AND status='pending'
            """,
            invoice_id
        )

        if updated != "UPDATE 0":

            await execute(
                """
                UPDATE users
                SET balance = balance + $1
                WHERE telegram_id=$2
                """,
                tx["paid_price"],
                tx["owner_id"]
            )

        # =========================
        # HAPUS QR
        # =========================
        try:
            if tx["qr_message_id"]:
                await call.bot.delete_message(
                    tx["qr_chat_id"],
                    tx["qr_message_id"]
                )
        except Exception:
            pass

        # =========================
        # KIRIM FILE
        # =========================
        sent = await send_page(
            bot=call.bot,
            chat_id=call.message.chat.id,
            user_id=tx["user_id"],
            code=tx["file_code"],
            page=1
        )

        if not sent:
            return await call.answer(
                "⚠️ Pembayaran berhasil, tetapi file gagal dikirim.",
                show_alert=True
            )

        try:
            await call.message.delete()
        except Exception:
            pass

        return await call.answer(
            "✅ Pembayaran berhasil",
            show_alert=True
        )

    except Exception:
        logger.exception(
            "Check payment failed | invoice=%s",
            invoice_id
        )

        return await call.answer(
            "❌ Terjadi kesalahan",
            show_alert=True
        )
