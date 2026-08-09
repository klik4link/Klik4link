import logging
import time
from io import BytesIO
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile
)
from database import fetchrow, execute
from utils.dompetx import DompetX
from utils.redis_client import safe_set, safe_delete
from handlers.admin_purchase import notify_admin_purchase
logger = logging.getLogger(__name__)
router = Router()
PAY_LOCK_TTL = 30
INVOICE_TTL = 3600
# =========================================================
# MENU PEMBAYARAN
# =========================================================
@router.callback_query(F.data.startswith("pay:"))
async def pay_menu(call: CallbackQuery):
    code = call.data.split(":", 1)[1]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Bayar Otomatis",
                    callback_data=f"auto_pay:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📲 Bayar Manual QR",
                    callback_data=f"manual_pay:{code}"
                )
            ]
        ]
    )
    await call.message.edit_text(
        "💳 <b>PILIH PEMBAYARAN</b>\n\n"
        "Silakan pilih metode pembayaran:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await call.answer()
# =========================================================
# DOMPETX AUTO PAYMENT
# =========================================================
@router.callback_query(F.data.startswith("auto_pay:"))
async def auto_pay(call: CallbackQuery):
    await call.answer(
        "⏳ Membuat pembayaran..."
    )
    user_id = call.from_user.id
    code = call.data.split(":", 1)[1]
    loading = await call.message.answer(
        "⏳ <b>Membuat pembayaran QRIS...</b>",
        parse_mode="HTML"
    )
    lock_key = (
        f"paylock:{user_id}:{code}"
    )
    try:
        # =================================================
        # PAYMENT LOCK
        # =================================================
        try:
            lock = await safe_set(
                lock_key,
                "1",
                ex=PAY_LOCK_TTL,
                nx=True
            )
        except Exception:
            logger.exception(
                "PAYMENT LOCK ERROR"
            )
            lock = True
        if not lock:
            try:
                await loading.delete()
            except Exception:
                pass
            return await call.answer(
                "Tunggu sebentar sebelum membuat pembayaran baru.",
                show_alert=True
            )
        # =================================================
        # GET FILE
        # =================================================
        file = await fetchrow(
            """
            SELECT
                owner_id,
                price,
                is_paid
            FROM files
            WHERE code=$1
            """,
            code
        )
        if not file:
            return await call.answer(
                "File tidak ditemukan.",
                show_alert=True
            )
        if not file["is_paid"]:
            return await call.answer(
                "File ini gratis.",
                show_alert=True
            )
        if file["owner_id"] == user_id:
            return await call.answer(
                "Owner tidak perlu membeli file sendiri.",
                show_alert=True
            )
        price = int(
            file["price"] or 0
        )
        if price <= 0:
            return await call.answer(
                "Harga file tidak valid.",
                show_alert=True
            )
        # =================================================
        # GENERATE MERCHANT REFERENCE
        # =================================================
        reference = (
            f"FILE-{user_id}-"
            f"{code}-"
            f"{int(time.time())}"
        )
        # =================================================
        # CREATE DOMPETX PAYMENT
        # =================================================
        data = await DompetX.create_payment(
            amount=price,
            description=f"File {code}",
            customer_name=call.from_user.full_name,
            reference=reference
        )
        if not data:
            return await call.answer(
                "Gagal membuat pembayaran DompetX.",
                show_alert=True
            )
        logger.info(
            "DOMPETX CREATE RESPONSE | %s",
            data
        )
        # =================================================
        # GET PAYMENT ID
        # =================================================
        payment_id = str(
            data.get("id", "")
        ).strip()
        if not payment_id:
            logger.error(
                "DompetX tidak mengembalikan payment ID | data=%s",
                data
            )
            return await call.answer(
                "Payment ID tidak ditemukan.",
                show_alert=True
            )
        # =================================================
        # GET STATUS
        # =================================================
        payment_status = str(
            data.get("status", "")
        ).lower()
        # =================================================
        # GET AMOUNT
        # =================================================
        amount = int(
            data.get(
                "amount",
                price
            )
            or price
        )
        # =================================================
        # GET QRIS IMAGE
        # =================================================
        qr_image = await DompetX.get_qr(
            payment_id
        )
        if not qr_image:
            logger.error(
                "QRIS DompetX gagal diambil | payment_id=%s",
                payment_id
            )
            return await call.answer(
                "QRIS gagal dibuat.",
                show_alert=True
            )
        # =================================================
        # SAVE PURCHASE
        # =================================================
        await execute(
            """
            INSERT INTO file_purchases
            (
                user_id,
                file_code,
                owner_id,
                paid_price,
                invoice_id,
                payment_id,
                status,
                created_at
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                $6,
                'pending',
                NOW()
            )
            """,
            user_id,
            code,
            file["owner_id"],
            price,
            reference,
            payment_id
        )
        # =================================================
        # ADMIN NOTIFY
        # =================================================
        try:
            await notify_admin_purchase(
                bot=call.bot,
                user_id=user_id,
                code=code,
                price=price
            )
        except Exception:
            logger.exception(
                "ADMIN PURCHASE NOTIFY ERROR"
            )
        # =================================================
        # REDIS INVOICE
        # =================================================
        try:
            await safe_set(
                f"invoice:{reference}",
                (
                    f"{user_id}:"
                    f"{code}:"
                    f"pending:"
                    f"{payment_id}"
                ),
                ex=INVOICE_TTL
            )
        except Exception:
            logger.exception(
                "REDIS INVOICE SAVE ERROR"
            )
        # =================================================
        # KEYBOARD
        # =================================================
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Check Payment",
                        callback_data=f"check:{payment_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Cancel",
                        callback_data=f"cancel:{payment_id}"
                    )
                ]
            ]
        )
        # =================================================
        # DELETE OLD MESSAGE
        # =================================================
        try:
            await call.message.delete()
        except Exception:
            pass
        # =================================================
        # SEND QRIS
        # =================================================
        msg = await call.message.answer_photo(
            BufferedInputFile(
                qr_image,
                filename="dompetx_qris.png"
            ),
            caption=(
                "⚡ <b>PAYMENT OTOMATIS</b>\n\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : "
                f"<b>Rp {amount:,}</b>\n"
                f"🧾 Invoice : "
                f"<code>{reference}</code>\n\n"
                "📲 Scan QRIS di atas untuk melakukan pembayaran.\n\n"
                "⏳ Setelah pembayaran berhasil, "
                "tekan <b>Check Payment</b> "
                "jika status belum otomatis berubah."
            ).replace(",", "."),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        # =================================================
        # SAVE QR MESSAGE
        # =================================================
        await execute(
            """
            UPDATE file_purchases
            SET
                qr_message_id=$1,
                qr_chat_id=$2
            WHERE payment_id=$3
            """,
            msg.message_id,
            msg.chat.id,
            payment_id
        )
        logger.info(
            "DOMPETX PAYMENT CREATED | "
            "user=%s | code=%s | reference=%s | "
            "payment_id=%s | amount=%s | status=%s",
            user_id,
            code,
            reference,
            payment_id,
            amount,
            payment_status
        )
    except Exception:
        logger.exception(
            "DOMPETX AUTO PAY ERROR"
        )
        try:
            await call.answer(
                "Terjadi kesalahan saat membuat pembayaran.",
                show_alert=True
            )
        except Exception:
            pass
    finally:
        try:
            await loading.delete()
        except Exception:
            pass
        try:
            await safe_delete(
                lock_key
            )
        except Exception:
            pass
# =========================================================
# BAYAR MANUAL QR
# =========================================================
@router.callback_query(F.data.startswith("manual_pay:"))
async def manual_pay(call: CallbackQuery):
    await call.answer(
        "⏳ Menyiapkan pembayaran..."
    )
    user_id = call.from_user.id
    code = call.data.split(":", 1)[1]
    loading = await call.message.answer(
        "⏳ <b>Menyiapkan QR Manual...</b>",
        parse_mode="HTML"
    )
    try:
        file = await fetchrow(
            """
            SELECT
                owner_id,
                price,
                is_paid
            FROM files
            WHERE code=$1
            """,
            code
        )
        if not file:
            return await call.answer(
                "File tidak ditemukan.",
                show_alert=True
            )
        if not file["is_paid"]:
            return await call.answer(
                "File gratis.",
                show_alert=True
            )
        if file["owner_id"] == user_id:
            return await call.answer(
                "Owner tidak perlu bayar.",
                show_alert=True
            )
        price = int(
            file["price"] or 0
        )
        if price <= 0:
            return await call.answer(
                "Harga file tidak valid.",
                show_alert=True
            )
        # =================================================
        # CREATE MANUAL INVOICE
        # =================================================
        invoice_id = (
            f"MANUAL-"
            f"{user_id}-"
            f"{code}-"
            f"{int(time.time())}"
        )
        await execute(
            """
            INSERT INTO file_purchases
            (
                user_id,
                file_code,
                owner_id,
                paid_price,
                invoice_id,
                status,
                created_at
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                'pending',
                NOW()
            )
            """,
            user_id,
            code,
            file["owner_id"],
            price,
            invoice_id
        )
        await safe_set(
            f"invoice:{invoice_id}",
            f"{user_id}:{code}:pending",
            ex=INVOICE_TTL
        )
        # =================================================
        # AMBIL QR MANUAL
        # =================================================
        from config import QR_PAYMENT
        qr_file = await call.bot.get_file(
            QR_PAYMENT
        )
        qr_download = await call.bot.download_file(
            qr_file.file_path
        )
        buf = BytesIO(
            qr_download.read()
        )
        buf.seek(0)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Saya Sudah Bayar",
                        callback_data=(
                            f"manual_check:{invoice_id}"
                        )
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Batal",
                        callback_data=(
                            f"cancel:{invoice_id}"
                        )
                    )
                ]
            ]
        )
        try:
            await call.message.delete()
        except Exception:
            pass
        msg = await call.message.answer_photo(
            BufferedInputFile(
                buf.getvalue(),
                filename="gopay.png"
            ),
            caption=(
                "📲 <b>PEMBAYARAN MANUAL</b>\n\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : "
                f"<b>Rp {price:,}</b>\n\n"
                "📷 Silakan scan QR Merchant di atas.\n\n"
                "⚠️ <b>PENTING!</b>\n"
                "• Nominal pembayaran <b>WAJIB</b> "
                "sama persis dengan nominal yang tertera.\n"
                "• Pembayaran kurang atau lebih "
                "tidak dapat diverifikasi otomatis.\n"
                "• Setelah transfer berhasil, "
                "tekan <b>✅ Saya Sudah Bayar</b>.\n"
                "• Admin akan memverifikasi pembayaran "
                "sebelum file dapat dibuka."
            ).replace(",", "."),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await execute(
            """
            UPDATE file_purchases
            SET
                qr_message_id=$1,
                qr_chat_id=$2
            WHERE invoice_id=$3
            """,
            msg.message_id,
            msg.chat.id,
            invoice_id
        )
    except Exception:
        logger.exception(
            "MANUAL PAY ERROR"
        )
    finally:
        try:
            await loading.delete()
        except Exception:
            pass
# =========================================================
# MANUAL PAYMENT CONFIRMATION
# =========================================================
@router.callback_query(
    F.data.startswith("manual_check:")
)
async def manual_check(call: CallbackQuery):
    invoice_id = (
        call.data.split(":", 1)[1]
    )
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
            "Invoice tidak ditemukan.",
            show_alert=True
        )
    if purchase["status"] == "paid":
        return await call.answer(
            "Pembayaran sudah disetujui.",
            show_alert=True
        )
    if purchase["status"] == "waiting_confirmation":
        return await call.answer(
            "Konfirmasi sudah dikirim ke admin.",
            show_alert=True
        )
    await execute(
        """
        UPDATE file_purchases
        SET
            status='waiting_confirmation'
        WHERE invoice_id=$1
        """,
        invoice_id
    )
    await notify_admin_purchase(
        bot=call.bot,
        user_id=purchase["user_id"],
        code=purchase["file_code"],
        price=purchase["paid_price"]
    )
    await call.message.edit_caption(
        caption=(
            "⏳ <b>MENUNGGU VERIFIKASI ADMIN</b>\n\n"
            "Konfirmasi pembayaran berhasil dikirim.\n\n"
            "Mohon tunggu admin melakukan "
            "pengecekan pembayaran.\n\n"
            "Setelah disetujui, file akan "
            "otomatis bisa dibuka."
        ),
        parse_mode="HTML",
        reply_markup=None
    )
    await call.answer(
        "Konfirmasi berhasil dikirim."
    )
