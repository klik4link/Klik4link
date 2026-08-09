import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from bot import bot
from config import CHANNEL_ID
from config_vip import VIP_PACKAGES
from database import get_pool
from utils.dompetx import DompetX
from utils.redis_client import redis_client
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/dompetx",
    tags=["DompetX"]
)
# =========================================================
# SUCCESS STATUS
# =========================================================
SUCCESS_STATUS = {
    "paid",
    "success",
    "settlement",
    "completed"
}
# =========================================================
# DOMPETX WEBHOOK
# =========================================================
@router.post("/webhook")
async def dompetx_webhook(
    request: Request
):
    # =====================================================
    # READ BODY
    # =====================================================
    body = await request.body()
    if not body:
        logger.warning(
            "DOMPETX WEBHOOK | EMPTY BODY"
        )
        return {
            "success": False,
            "message": "Empty body"
        }
    # =====================================================
    # PARSE JSON
    # =====================================================
    try:
        data = await request.json()
    except Exception:
        logger.exception(
            "DOMPETX WEBHOOK | INVALID JSON"
        )
        return {
            "success": False,
            "message": "Invalid JSON"
        }
    if not isinstance(data, dict):
        logger.error(
            "DOMPETX WEBHOOK | INVALID DATA TYPE"
        )
        return {
            "success": False,
            "message": "Invalid webhook data"
        }
    logger.info(
        "DOMPETX WEBHOOK RECEIVED | %s",
        data
    )
    # =====================================================
    # EXTRACT TRANSACTION
    # =====================================================
    transaction = (
        data.get("transaction")
        or {}
    )
    if not isinstance(
        transaction,
        dict
    ):
        transaction = {}
    # =====================================================
    # PAYMENT ID
    # =====================================================
    payment_id = (
        data.get("id")
        or data.get("payment_id")
        or data.get("paymentId")
        or transaction.get("id")
        or transaction.get("payment_id")
        or transaction.get("paymentId")
    )
    # =====================================================
    # MERCHANT REFERENCE
    # =====================================================
    reference = (
        data.get("reference")
        or data.get("reference_id")
        or data.get("referenceId")
        or transaction.get("reference")
        or transaction.get("reference_id")
        or transaction.get("referenceId")
    )
    # =====================================================
    # WEBHOOK STATUS
    # =====================================================
    webhook_status = (
        data.get("status")
        or transaction.get("status")
        or ""
    )
    webhook_status = str(
        webhook_status
    ).lower().strip()
    logger.info(
        "DOMPETX WEBHOOK | "
        "payment_id=%s reference=%s status=%s",
        payment_id,
        reference,
        webhook_status
    )
    # =====================================================
    # IDENTIFIER REQUIRED
    # =====================================================
    if not payment_id and not reference:
        logger.error(
            "DOMPETX WEBHOOK | "
            "PAYMENT ID AND REFERENCE MISSING"
        )
        return {
            "success": False,
            "message": "Payment identifier missing"
        }
    # =====================================================
    # VERIFY PAYMENT DIRECTLY TO DOMPETX
    # =====================================================
    verified = None
    try:
        if payment_id:
            verified = (
                await DompetX.check_payment(
                    payment_id
                )
            )
        elif reference:
            verified = (
                await DompetX.check_by_reference(
                    reference
                )
            )
    except Exception:
        logger.exception(
            "DOMPETX PAYMENT VERIFICATION ERROR"
        )
        return {
            "success": False,
            "message": "Payment verification failed"
        }
    if not verified:
        logger.error(
            "DOMPETX PAYMENT VERIFICATION FAILED | "
            "payment_id=%s reference=%s",
            payment_id,
            reference
        )
        return {
            "success": False,
            "message": "Unable to verify payment"
        }
    logger.info(
        "DOMPETX VERIFIED RESPONSE | %s",
        verified
    )
    # =====================================================
    # EXTRACT VERIFIED TRANSACTION
    # =====================================================
    verified_transaction = (
        verified.get("transaction")
        if isinstance(
            verified,
            dict
        )
        else {}
    )
    if not isinstance(
        verified_transaction,
        dict
    ):
        verified_transaction = {}
    # =====================================================
    # VERIFIED PAYMENT ID
    # =====================================================
    verified_payment_id = (
        verified.get("id")
        or verified.get("payment_id")
        or verified.get("paymentId")
        or verified_transaction.get("id")
        or verified_transaction.get("payment_id")
        or verified_transaction.get("paymentId")
        or payment_id
    )
    # =====================================================
    # VERIFIED REFERENCE
    # =====================================================
    verified_reference = (
        verified.get("reference")
        or verified.get("reference_id")
        or verified.get("referenceId")
        or verified_transaction.get("reference")
        or verified_transaction.get("reference_id")
        or verified_transaction.get("referenceId")
        or reference
    )
    # =====================================================
    # VERIFIED STATUS
    # =====================================================
    verified_status = (
        verified.get("status")
        or verified_transaction.get("status")
        or ""
    )
    verified_status = str(
        verified_status
    ).lower().strip()
    logger.info(
        "DOMPETX VERIFIED | "
        "payment_id=%s reference=%s status=%s",
        verified_payment_id,
        verified_reference,
        verified_status
    )
    # =====================================================
    # ONLY PROCESS SUCCESS
    # =====================================================
    if verified_status not in SUCCESS_STATUS:
        logger.info(
            "DOMPETX PAYMENT NOT SUCCESS | "
            "status=%s",
            verified_status
        )
        return {
            "success": True,
            "status": verified_status
        }
    # =====================================================
    # REFERENCE REQUIRED
    # =====================================================
    invoice_id = verified_reference
    if not invoice_id:
        logger.error(
            "DOMPETX VERIFIED PAYMENT "
            "WITHOUT REFERENCE"
        )
        return {
            "success": False,
            "message": "Reference missing"
        }
    # =====================================================
    # REDIS PROCESSING LOCK
    # =====================================================
    lock_key = (
        f"payment_processing:{invoice_id}"
    )
    if await redis_client.get(
        lock_key
    ):
        logger.info(
            "DOMPETX PAYMENT ALREADY PROCESSING | %s",
            invoice_id
        )
        return {
            "success": True,
            "message": "Already processing"
        }
    await redis_client.set(
        lock_key,
        "1",
        ex=300
    )
    pool = await get_pool()
    try:
        # =================================================
        # FILE PAYMENT
        # =================================================
        purchase = await pool.fetchrow(
            """
            SELECT *
            FROM file_purchases
            WHERE invoice_id=$1
            """,
            invoice_id
        )
        if purchase:
            return await process_file_payment(
                pool=pool,
                purchase=purchase,
                invoice_id=invoice_id,
                payment_id=verified_payment_id
            )
        # =================================================
        # VIP PAYMENT
        # =================================================
        trx = await pool.fetchrow(
            """
            SELECT *
            FROM payments
            WHERE invoice_id=$1
            """,
            invoice_id
        )
        if trx:
            return await process_vip_payment(
                pool=pool,
                trx=trx,
                invoice_id=invoice_id,
                payment_id=verified_payment_id
            )
        # =================================================
        # PAYMENT NOT FOUND
        # =================================================
        logger.warning(
            "DOMPETX PAYMENT NOT FOUND | "
            "invoice=%s payment_id=%s",
            invoice_id,
            verified_payment_id
        )
        return {
            "success": False,
            "message": "Payment record not found"
        }
    except Exception:
        logger.exception(
            "DOMPETX WEBHOOK PROCESSING ERROR | "
            "invoice=%s",
            invoice_id
        )
        return {
            "success": False,
            "message": "Processing error"
        }
    finally:
        try:
            await redis_client.delete(
                lock_key
            )
        except Exception:
            logger.exception(
                "DOMPETX LOCK DELETE ERROR | %s",
                invoice_id
            )
# =========================================================
# PROCESS FILE PAYMENT
# =========================================================
async def process_file_payment(
    pool,
    purchase,
    invoice_id: str,
    payment_id: str | None = None
):
    # =====================================================
    # GET FILE
    # =====================================================
    file = await pool.fetchrow(
        """
        SELECT *
        FROM files
        WHERE code=$1
        """,
        purchase["file_code"]
    )
    if not file:
        logger.error(
            "FILE NOT FOUND | code=%s",
            purchase["file_code"]
        )
        return {
            "success": False,
            "message": "File not found"
        }
    # =====================================================
    # ALREADY PAID
    # =====================================================
    if purchase["status"] == "paid":
        logger.info(
            "FILE PAYMENT ALREADY PAID | "
            "invoice=%s",
            invoice_id
        )
        if (
            payment_id
            and not purchase["payment_id"]
        ):
            await pool.execute(
                """
                UPDATE file_purchases
                SET payment_id=$1
                WHERE invoice_id=$2
                """,
                payment_id,
                invoice_id
            )
        return {
            "success": True,
            "message": "Already paid"
        }
    # =====================================================
    # PRICE
    # =====================================================
    price = int(
        file["price"]
        or purchase["paid_price"]
        or 0
    )
    if price <= 0:
        logger.error(
            "INVALID FILE PRICE | "
            "invoice=%s price=%s",
            invoice_id,
            price
        )
        return {
            "success": False,
            "message": "Invalid payment amount"
        }
    # =====================================================
    # SELLER INCOME
    # =====================================================
    income = int(
        price * 0.90
    )
    # =====================================================
    # DATABASE TRANSACTION
    # =====================================================
    async with pool.acquire() as conn:
        async with conn.transaction():
            # ---------------------------------------------
            # LOCK PURCHASE
            # ---------------------------------------------
            locked_purchase = await conn.fetchrow(
                """
                SELECT *
                FROM file_purchases
                WHERE invoice_id=$1
                FOR UPDATE
                """,
                invoice_id
            )
            if not locked_purchase:
                logger.error(
                    "PURCHASE NOT FOUND AFTER LOCK | %s",
                    invoice_id
                )
                return {
                    "success": False,
                    "message": "Purchase not found"
                }
            # ---------------------------------------------
            # DUPLICATE PROTECTION
            # ---------------------------------------------
            if locked_purchase["status"] == "paid":
                logger.info(
                    "FILE PAYMENT ALREADY PAID "
                    "AFTER LOCK | %s",
                    invoice_id
                )
                return {
                    "success": True,
                    "message": "Already paid"
                }
            # ---------------------------------------------
            # MARK PAID
            # ---------------------------------------------
            await conn.execute(
                """
                UPDATE file_purchases
                SET
                    status='paid',
                    payment_id=COALESCE($1, payment_id),
                    paid_at=NOW()
                WHERE invoice_id=$2
                """,
                payment_id,
                invoice_id
            )
            # ---------------------------------------------
            # ADD SELLER BALANCE
            # ---------------------------------------------
            result = await conn.execute(
                """
                UPDATE users
                SET
                    balance=COALESCE(balance,0)+$1,
                    total_sales=COALESCE(total_sales,0)+1,
                    total_income=COALESCE(total_income,0)+$1
                WHERE telegram_id=$2
                """,
                income,
                file["owner_id"]
            )
            logger.info(
                "SELLER BALANCE UPDATE | "
                "result=%s owner=%s income=%s",
                result,
                file["owner_id"],
                income
            )
    # =====================================================
    # SUCCESS LOG
    # =====================================================
    logger.info(
        "FILE PAYMENT SUCCESS | "
        "invoice=%s payment_id=%s owner=%s income=%s",
        invoice_id,
        payment_id,
        file["owner_id"],
        income
    )
    # =====================================================
    # DELETE REDIS INVOICE
    # =====================================================
    try:
        await redis_client.delete(
            f"invoice:{invoice_id}"
        )
    except Exception:
        logger.exception(
            "REDIS INVOICE DELETE ERROR"
        )
    # =====================================================
    # DELETE QR MESSAGE
    # =====================================================
    try:
        qr_chat_id = (
            purchase["qr_chat_id"]
        )
        qr_message_id = (
            purchase["qr_message_id"]
        )
        if qr_chat_id and qr_message_id:
            await bot.delete_message(
                chat_id=qr_chat_id,
                message_id=qr_message_id
            )
            logger.info(
                "QR MESSAGE DELETED | invoice=%s",
                invoice_id
            )
    except Exception:
        logger.exception(
            "DELETE QR MESSAGE ERROR | "
            "invoice=%s",
            invoice_id
        )
    # =====================================================
    # OWNER NOTIFICATION
    # =====================================================
    try:
        await bot.send_message(
            file["owner_id"],
            (
                "💰 <b>FILE TERJUAL</b>\n\n"
                f"📂 File : "
                f"<code>{purchase['file_code']}</code>\n"
                f"💵 Masuk : "
                f"Rp {income:,}"
            ).replace(",", "."),
            parse_mode="HTML"
        )
    except Exception:
        logger.exception(
            "OWNER NOTIFY ERROR"
        )
    # =====================================================
    # CHANNEL NOTIFICATION
    # =====================================================
    try:
        await bot.send_message(
            CHANNEL_ID,
            (
                "✅ <b>SOLD OUT FILE</b>\n\n"
                f"📂 File : "
                f"<code>{purchase['file_code']}</code>\n"
                f"👤 User : "
                f"<code>{purchase['user_id']}</code>\n"
                f"💰 Harga : "
                f"Rp {price:,}\n"
                f"🧾 Invoice : "
                f"<code>{invoice_id}</code>"
            ).replace(",", "."),
            parse_mode="HTML"
        )
    except Exception:
        logger.exception(
            "CHANNEL NOTIFY ERROR"
        )
    # =====================================================
    # SEND OPEN FILE BUTTON
    # =====================================================
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📂 OPEN FILE",
                        callback_data=(
                            f"page:"
                            f"{purchase['file_code']}:1"
                        )
                    )
                ]
            ]
        )
        await bot.send_message(
            purchase["user_id"],
            (
                "✅ <b>PEMBAYARAN BERHASIL!</b>\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "📦 <b>File sudah tersedia</b>\n\n"
                "Klik tombol di bawah "
                "untuk membuka file.\n\n"
                "━━━━━━━━━━━━━━"
            ),
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        logger.exception(
            "SEND OPEN FILE BUTTON ERROR"
        )
    return {
        "success": True,
        "message": "File payment processed"
    }
# =========================================================
# PROCESS VIP PAYMENT
# =========================================================
async def process_vip_payment(
    pool,
    trx,
    invoice_id: str,
    payment_id: str | None = None
):
    # =====================================================
    # ALREADY PAID
    # =====================================================
    if trx["status"] == "paid":
        logger.info(
            "VIP PAYMENT ALREADY PAID | "
            "invoice=%s",
            invoice_id
        )
        return {
            "success": True,
            "message": "Already paid"
        }
    # =====================================================
    # GET VIP PACKAGE
    # =====================================================
    paket = VIP_PACKAGES.get(
        trx["code"]
    )
    if not paket:
        logger.error(
            "VIP PACKAGE NOT FOUND | code=%s",
            trx["code"]
        )
        return {
            "success": False,
            "message": "VIP package not found"
        }
    # =====================================================
    # GET USER
    # =====================================================
    user = await pool.fetchrow(
        """
        SELECT
            vip,
            vip_until
        FROM users
        WHERE telegram_id=$1
        """,
        trx["user_id"]
    )
    if not user:
        logger.error(
            "VIP USER NOT FOUND | user=%s",
            trx["user_id"]
        )
        return {
            "success": False,
            "message": "User not found"
        }
    # =====================================================
    # CURRENT TIME
    # =====================================================
    now = datetime.now(
        timezone.utc
    )
    # =====================================================
    # CURRENT VIP EXPIRATION
    # =====================================================
    current_vip_until = (
        user["vip_until"]
    )
    # PostgreSQL TIMESTAMP WITHOUT TIME ZONE
    # menghasilkan datetime naive.
    #
    # Normalisasi ke UTC agar aman dibandingkan
    # dengan datetime timezone-aware.
    if current_vip_until:
        if current_vip_until.tzinfo is None:
            current_vip_until = (
                current_vip_until.replace(
                    tzinfo=timezone.utc
                )
            )
    # =====================================================
    # CALCULATE NEW VIP EXPIRATION
    # =====================================================
    if (
        current_vip_until
        and current_vip_until > now
    ):
        vip_until = (
            current_vip_until
            +
            timedelta(
                days=paket["days"]
            )
        )
    else:
        vip_until = (
            now
            +
            timedelta(
                days=paket["days"]
            )
        )
    # =====================================================
    # DATABASE TRANSACTION
    # =====================================================
    async with pool.acquire() as conn:
        async with conn.transaction():
            # ---------------------------------------------
            # LOCK PAYMENT
            # ---------------------------------------------
            locked_trx = await conn.fetchrow(
                """
                SELECT *
                FROM payments
                WHERE invoice_id=$1
                FOR UPDATE
                """,
                invoice_id
            )
            if not locked_trx:
                logger.error(
                    "VIP PAYMENT NOT FOUND | %s",
                    invoice_id
                )
                return {
                    "success": False,
                    "message": "Payment not found"
                }
            # ---------------------------------------------
            # DUPLICATE PROTECTION
            # ---------------------------------------------
            if locked_trx["status"] == "paid":
                return {
                    "success": True,
                    "message": "Already paid"
                }
            # ---------------------------------------------
            # MARK PAYMENT PAID
            # ---------------------------------------------
            await conn.execute(
                """
                UPDATE payments
                SET
                    status='paid'
                WHERE invoice_id=$1
                """,
                invoice_id
            )
            # ---------------------------------------------
            # ACTIVATE VIP
            # ---------------------------------------------
            await conn.execute(
                """
                UPDATE users
                SET
                    vip=TRUE,
                    vip_until=$1
                WHERE telegram_id=$2
                """,
                vip_until,
                trx["user_id"]
            )
    # =====================================================
    # SUCCESS LOG
    # =====================================================
    logger.info(
        "VIP PAYMENT SUCCESS | "
        "invoice=%s payment_id=%s user=%s",
        invoice_id,
        payment_id,
        trx["user_id"]
    )
    # =====================================================
    # DELETE REDIS INVOICE
    # =====================================================
    try:
        await redis_client.delete(
            f"invoice:{invoice_id}"
        )
    except Exception:
        logger.exception(
            "VIP REDIS DELETE ERROR"
        )
    # =====================================================
    # USER NOTIFICATION
    # =====================================================
    try:
        await bot.send_message(
            trx["user_id"],
            (
                "🎉 <b>VIP ACTIVE</b>\n\n"
                f"📦 Paket : {paket['name']}\n"
                f"⏰ Expired : "
                f"{vip_until:%d-%m-%Y %H:%M UTC}"
            ),
            parse_mode="HTML"
        )
    except Exception:
        logger.exception(
            "VIP USER NOTIFY ERROR"
        )
    # =====================================================
    # CHANNEL NOTIFICATION
    # =====================================================
    try:
        await bot.send_message(
            CHANNEL_ID,
            (
                "💎 <b>VIP SOLD</b>\n\n"
                f"👤 User : "
                f"<code>{trx['user_id']}</code>\n"
                f"📦 Paket : "
                f"{paket['name']}\n"
                f"🧾 Invoice : "
                f"<code>{invoice_id}</code>"
            ),
            parse_mode="HTML"
        )
    except Exception:
        logger.exception(
            "VIP CHANNEL NOTIFY ERROR"
        )
    return {
        "success": True,
        "message": "VIP payment processed"
    }
