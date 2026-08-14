from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging
from database import fetchrow, execute
from handlers.page import send_page
from utils.dompetx import DompetX
from utils.redis_client import safe_delete
from bot import bot
logger = logging.getLogger(__name__)
router = Router()
CHANNEL_PAYMENT = -1004413314849
# =========================================================
# STATUS BERHASIL DOMPETX
# =========================================================
SUCCESS_STATUS = {
    "paid",
    "success",
    "settlement",
    "completed",
    "completed_payment"
}
STATUS_MAP = {
    "pending": "⏳ Menunggu pembayaran",
    "processing": "⏳ Pembayaran sedang diproses",
    "created": "⏳ Menunggu pembayaran",
    "expired": "❌ Pembayaran kadaluarsa",
    "cancelled": "❌ Pembayaran dibatalkan",
    "failed": "❌ Pembayaran gagal",
}
# =========================================================
# CHECK PAYMENT
# =========================================================
@router.callback_query(F.data.startswith("check:"))
async def check_payment(call: CallbackQuery):
    invoice_id = call.data.split(":", 1)[1]
    try:
        logger.info(
            "CHECK PAYMENT | invoice=%s | user=%s",
            invoice_id,
            call.from_user.id
        )
        # =================================================
        # AMBIL TRANSAKSI DARI DATABASE
        # =================================================
        tx = await fetchrow(
            """
            SELECT
                id,
                user_id,
                owner_id,
                paid_price,
                file_code,
                status,
                invoice_id,
                payment_id,
                qr_message_id,
                qr_chat_id,
                paid_at
            FROM file_purchases
            WHERE invoice_id=$1
            LIMIT 1
            """,
            invoice_id
        )
        if not tx:
            return await call.answer(
                "❌ Invoice tidak ditemukan.",
                show_alert=True
            )
        # =================================================
        # JIKA SUDAH PAID
        # =================================================
        if tx["status"] == "paid":
            logger.info(
                "ALREADY PAID | invoice=%s",
                invoice_id
            )
            try:
                await call.message.delete()
            except Exception:
                pass
            sent = await send_page(
                bot=call.bot,
                chat_id=call.message.chat.id,
                user_id=tx["user_id"],
                code=tx["file_code"],
                page=1
            )
            if sent:
                return await call.answer(
                    "✅ File berhasil dikirim."
                )
            return await call.answer(
                "⚠️ Pembayaran sudah berhasil, tetapi file gagal dikirim.",
                show_alert=True
            )
        # =================================================
        # PAYMENT ID WAJIB ADA
        # =================================================
        payment_id = tx["payment_id"]
        if not payment_id:
            logger.error(
                "PAYMENT ID MISSING | invoice=%s",
                invoice_id
            )
            return await call.answer(
                "❌ ID pembayaran tidak ditemukan.",
                show_alert=True
            )
        # =================================================
        # CEK STATUS DOMPETX
        # =================================================
        try:
            data = await DompetX.check_payment(
                payment_id
            )
        except Exception:
            logger.exception(
                "DOMPETX CHECK ERROR | payment_id=%s",
                payment_id
            )
            return await call.answer(
                "❌ Gagal menghubungi payment gateway.",
                show_alert=True
            )
        if not data:
            return await call.answer(
                "❌ Gagal mendapatkan status pembayaran.",
                show_alert=True
            )
        logger.info(
            "DOMPETX CHECK RESPONSE | payment_id=%s | data=%s",
            payment_id,
            data
        )
        # =================================================
        # AMBIL STATUS
        # =================================================
        status = str(
            data.get("status")
            or data.get("payment_status")
            or data.get("transaction_status")
            or ""
        ).lower().strip()
        logger.info(
            "DOMPETX STATUS | invoice=%s | payment_id=%s | status=%s",
            invoice_id,
            payment_id,
            status
        )
        # =================================================
        # BELUM BERHASIL
        # =================================================
        if status not in SUCCESS_STATUS:
            message = STATUS_MAP.get(
                status,
                "⏳ Menunggu pembayaran"
            )
            return await call.answer(
                message,
                show_alert=True
            )
        # =================================================
        # VERIFIKASI NOMINAL
        # =================================================
        gateway_amount = (
            data.get("amount")
            or data.get("amount_total")
            or data.get("paid_amount")
        )
        if gateway_amount is not None:
            try:
                gateway_amount = int(
                    float(gateway_amount)
                )
                expected_amount = int(
                    tx["paid_price"]
                )
                if gateway_amount != expected_amount:
                    logger.error(
                        "AMOUNT MISMATCH | invoice=%s | expected=%s | received=%s",
                        invoice_id,
                        expected_amount,
                        gateway_amount
                    )
                    return await call.answer(
                        "❌ Nominal pembayaran tidak sesuai.",
                        show_alert=True
                    )
            except (TypeError, ValueError):
                logger.warning(
                    "INVALID GATEWAY AMOUNT | invoice=%s | amount=%s",
                    invoice_id,
                    gateway_amount
                )
        # =================================================
        # TRANSACTION DATABASE
        # =================================================
        # Lock sederhana berdasarkan status pending.
        # Hanya transaksi yang masih pending yang boleh diproses.
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
        logger.info(
            "FILE PURCHASE UPDATE | invoice=%s | result=%s",
            invoice_id,
            updated
        )
        # =================================================
        # TAMBAH SALDO OWNER
        # HANYA JIKA UPDATE BERHASIL
        # =================================================
        if updated == "UPDATE 1":
            # Owner menerima 90%
            income = int(
                tx["paid_price"] * 0.9
            )
            await execute(
                """
                UPDATE users
                SET
                    balance = COALESCE(balance, 0) + $1
                WHERE telegram_id=$2
                """,
                income,
                tx["owner_id"]
            )
            logger.info(
                "OWNER BALANCE UPDATED | owner=%s | income=%s | invoice=%s",
                tx["owner_id"],
                income,
                invoice_id
            )
        else:
            logger.info(
                "BALANCE NOT UPDATED - ALREADY PROCESSED | invoice=%s",
                invoice_id
            )
        # =================================================
        # HAPUS REDIS INVOICE
        # =================================================
        try:
            await safe_delete(
                f"invoice:{invoice_id}"
            )
        except Exception:
            logger.exception(
                "REDIS INVOICE DELETE ERROR | invoice=%s",
                invoice_id
            )
        # =================================================
        # HAPUS QR PAYMENT
        # =================================================
        try:
            if (
                tx["qr_chat_id"]
                and tx["qr_message_id"]
            ):
                await call.bot.delete_message(
                    chat_id=tx["qr_chat_id"],
                    message_id=tx["qr_message_id"]
                )
                logger.info(
                    "QR DELETED | invoice=%s",
                    invoice_id
                )
        except Exception:
            logger.warning(
                "QR DELETE FAILED | invoice=%s",
                invoice_id
            )
        # =================================================
        # KIRIM FILE
        # =================================================
        sent = await send_page(
            bot=call.bot,
            chat_id=call.message.chat.id,
            user_id=tx["user_id"],
            code=tx["file_code"],
            page=1
        )
        if not sent:
            logger.error(
                "FILE SEND FAILED | invoice=%s | file=%s",
                invoice_id,
                tx["file_code"]
            )
            return await call.answer(
                "⚠️ Pembayaran berhasil, tetapi file gagal dikirim.",
                show_alert=True
            )
        # =================================================
        # CHANNEL NOTIFICATION
        # =================================================
        try:
            income = int(
                tx["paid_price"] * 0.9
            )
            await bot.send_message(
                chat_id=CHANNEL_PAYMENT,
                text=(
                    "💰 <b>PEMBAYARAN BERHASIL</b>\n\n"
                    f"👤 Pembeli : "
                    f"<code>{tx['user_id']}</code>\n"
                    f"📁 File : "
                    f"<code>{tx['file_code']}</code>\n"
                    f"💵 Harga : "
                    f"Rp {tx['paid_price']:,}\n"
                    f"💰 Owner menerima : "
                    f"Rp {income:,}\n"
                    f"🧾 Invoice : "
                    f"<code>{invoice_id}</code>\n"
                    f"🆔 Payment ID : "
                    f"<code>{payment_id}</code>\n\n"
                    "✅ File berhasil dikirim."
                ).replace(",", "."),
                parse_mode="HTML"
            )
        except Exception:
            logger.exception(
                "CHANNEL PAYMENT POST FAILED | invoice=%s",
                invoice_id
            )
        # =================================================
        # HAPUS PESAN QR / CHECK
        # =================================================
        try:
            await call.message.delete()
        except Exception:
            pass
        logger.info(
            "PAYMENT SUCCESS | invoice=%s | payment_id=%s",
            invoice_id,
            payment_id
        )
        return await call.answer(
            "✅ Pembayaran berhasil!"
        )
    except Exception:
        logger.exception(
            "CHECK PAYMENT FAILED | invoice=%s",
            invoice_id
        )
        return await call.answer(
            "❌ Terjadi kesalahan saat mengecek pembayaran.",
            show_alert=True
        )
