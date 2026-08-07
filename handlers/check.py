from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging

from database import fetchrow, execute
from handlers.page import send_page
from utils.bayargg import BayarGG
from bot import bot


logger = logging.getLogger(__name__)

router = Router()


CHANNEL_PAYMENT = -1003894841696


SUCCESS_STATUS = [
    "paid",
    "success",
    "settlement",
    "completed"
]


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
        # CEK PAYMENT BAYARGG
        # =========================

        try:

            data = await BayarGG.check_payment(
                invoice_id
            )

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


        logger.info(
            "BAYARGG RESPONSE | %s",
            data
        )



        # =========================
        # AMBIL DATA TRANSAKSI
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
        # JIKA SUDAH PAID
        # =========================

        if tx["status"] == "paid":

            sent = await send_page(
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

        if status not in SUCCESS_STATUS:

            return await call.answer(
                status_map.get(
                    status,
                    "⏳ Menunggu pembayaran"
                ),
                show_alert=True
            )



        # =========================
        # UPDATE STATUS PAID
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



        # tambah saldo owner hanya sekali

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


        logger.info(
            "PAYMENT SUCCESS DATABASE | %s",
            invoice_id
        )



        # =========================
        # HAPUS QR
        # =========================

        try:

            if tx["qr_message_id"]:

                await call.bot.delete_message(
                    chat_id=tx["qr_chat_id"],
                    message_id=tx["qr_message_id"]
                )

        except Exception:

            logger.warning(
                "QR DELETE FAILED"
            )



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
                "⚠️ Pembayaran berhasil, file gagal dikirim.",
                show_alert=True
            )



        # =========================
        # POST CHANNEL
        # =========================

        try:

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
                    f"🧾 Invoice : "
                    f"<code>{invoice_id}</code>\n\n"
                    "✅ File berhasil dikirim."
                ).replace(",", "."),
                parse_mode="HTML"
            )


            logger.info(
                "CHANNEL PAYMENT POST SUCCESS | %s",
                invoice_id
            )


        except Exception:

            logger.exception(
                "CHANNEL PAYMENT POST FAILED"
            )



        # =========================
        # HAPUS PESAN QR USER
        # =========================

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
