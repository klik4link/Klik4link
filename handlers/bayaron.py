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
# DOMPETX WEBHOOK
# =========================================================
@router.post("/webhook")
async def dompetx_webhook(request: Request):
    # =====================================================
    # READ BODY
    # =====================================================
    body = await request.body()
    if not body:
        logger.warning(
            "DOMPETX WEBHOOK EMPTY BODY"
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
            "DOMPETX WEBHOOK INVALID JSON"
        )
        return {
            "success": False,
            "message": "Invalid JSON"
        }
    logger.info(
        "DOMPETX WEBHOOK RECEIVED | %s",
        data
    )
    # =====================================================
    # GET PAYMENT DATA
    # =====================================================
    transaction = data.get(
        "transaction"
    ) or {}
    # DompetX documentation can return transaction
    # information depending on webhook implementation.
    #
    # Support several possible locations so the handler
    # remains tolerant.
    payment_id = (
        data.get("id")
        or data.get("payment_id")
        or transaction.get("id")
        or transaction.get("payment_id")
    )
    reference = (
        data.get("reference")
        or data.get("reference_id")
        or transaction.get("reference")
        or transaction.get("reference_id")
    )
    webhook_status = (
        data.get("status")
        or transaction.get("status")
        or ""
    )
    webhook_status = str(
        webhook_status
    ).lower().strip()
    logger.info(
        "DOMPETX WEBHOOK | payment_id=%s reference=%s status=%s",
        payment_id,
        reference,
        webhook_status
    )
    # =====================================================
    # IDENTIFIER REQUIRED
    # =====================================================
    if not payment_id and not reference:
        logger.error(
            "DOMPETX WEBHOOK WITHOUT PAYMENT ID / REFERENCE"
        )
        return {
            "success": False,
            "message": "Payment identifier missing"
        }
    # =====================================================
    # VERIFY PAYMENT DIRECTLY TO DOMPETX
    # =====================================================
    #
    # Jangan langsung percaya status webhook.
    #
    # Kita query DompetX untuk memastikan transaksi benar-benar
    # sudah paid.
    #
    # Jika payment_id tersedia -> check by ID.
    # Jika tidak -> check by merchant reference.
    # =====================================================
    verified = None
    try:
        if payment_id:
            verified = await DompetX.check_payment(
                payment_id
            )
        elif reference:
            verified = await DompetX.check_by_reference(
                reference
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
            "DOMPETX PAYMENT VERIFICATION FAILED | payment_id=%s reference=%s",
            payment_id,
            reference
        )
        return {
            "success": False,
            "message": "Unable to verify payment"
        }
    # =====================================================
    # GET VERIFIED TRANSACTION
    # =====================================================
    verified_transaction = (
        verified.get("transaction")
        if isinstance(
            verified,
            dict
        )
        else None
    )
    if not isinstance(
        verified_transaction,
        dict
    ):
        verified_transaction = {}
    verified_payment_id = (
        verified.get("id")
        or verified.get("payment_id")
        or verified_transaction.get("id")
        or verified_transaction.get("payment_id")
        or payment_id
    )
    verified_reference = (
        verified.get("reference")
        or verified.get("reference_id")
        or verified_transaction.get("reference")
        or verified_transaction.get("reference_id")
        or reference
    )
    verified_status = (
        verified.get("status")
        or verified_transaction.get("status")
        or ""
    )
    verified_status = str(
        verified_status
    ).lower().strip()
    logger.info(
        "DOMPETX VERIFIED | payment_id=%s reference=%s status=%s",
        verified_payment_id,
        verified_reference,
        verified_status
    )
    # =====================================================
    # ONLY PROCESS PAID
    # =====================================================
    if verified_status != "paid":
        logger.info(
            "DOMPETX PAYMENT NOT PAID | status=%s",
            verified_status
        )
        return {
            "success": True,
            "status": verified_status
        }
    # =====================================================
    # IDENTIFIER FOR DATABASE
    # =====================================================
    invoice_id = verified_reference
    if not invoice_id:
        logger.error(
            "DOMPETX VERIFIED PAYMENT WITHOUT REFERENCE"
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
            "success": True
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
            "DOMPETX PAYMENT NOT FOUND | invoice=%s payment_id=%s",
            invoice_id,
            verified_payment_id
        )
        return {
            "success": False,
            "message": "Payment record not found"
        }
    except Exception:
        logger.exception(
            "DOMPETX WEBHOOK PROCESSING ERROR | invoice=%s",
            invoice_id
        )
        return {
            "success": False,
            "message": "Processing error"
        }
    finally:
        await redis_client.delete(
            lock_key
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
            "FILE PAYMENT ALREADY PAID | invoice=%s",
            invoice_id
        )
        # Tetap simpan payment_id jika sebelumnya kosong.
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
    # CALCULATE SELLER INCOME
    # =====================================================
    price = int(
        file["price"] or
        purchase["paid_price"] or
        0
    )
    income = int(
        price * 0.9
    )
    # =====================================================
    # DATABASE TRANSACTION
    # =====================================================
    async with pool.acquire() as conn:
        async with conn.transaction():
            # ---------------------------------------------
            # Lock purchase row
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
                    "PURCHASE DISAPPEARED | invoice=%s",
                    invoice_id
                )
                return {
                    "success": False,
                    "message": "Purchase not found"
                }
            # ---------------------------------------------
            # Duplicate protection
            # ---------------------------------------------
            if locked_purchase["status"] == "paid":
                logger.info(
                    "FILE PAYMENT ALREADY PAID AFTER LOCK | invoice=%s",
                    invoice_id
                )
                return {
                    "success": True,
                    "message": "Already paid"
                }
            # ---------------------------------------------
            # Mark paid
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
            # Seller balance
            # ---------------------------------------------
            await conn.execute(
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
        "FILE PAYMENT SUCCESS | invoice=%s payment_id=%s owner=%s income=%s",
        invoice_id,
        payment_id,
        file["owner_id"],
        income
    )
    # =====================================================
    # DELETE REDIS INVOICE
    # =====================================================
    await redis_client.delete(
        f"invoice:{invoice_id}"
    )
    # =====================================================
    # DELETE QR MESSAGE
    # =====================================================
    try:
        if (
            purchase["qr_chat_id"]
            and purchase["qr_message_id"]
        ):
            await bot.delete_message(
                chat_id=purchase["qr_chat_id"],
                message_id=purchase["qr_message_id"]
            )
            logger.info(
                "QR MESSAGE DELETED | invoice=%s",
                invoice_id
            )
    except Exception:
        logger.exception(
            "DELETE QR MESSAGE ERROR | invoice=%s",
            invoice_id
        )
    # =====================================================
    # OWNER NOTIFICATION
    # =====================================================
    try:
        await bot.send_message(
            file["owner_id"],
            (
                "💰 <b>File Terjual</b>\n\n"
                f"📂 File : <code>{purchase['file_code']}</code>\n"
                f"💵 Masuk : Rp {income:,}"
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
                f"📂 File : <code>{purchase['file_code']}</code>\n"
                f"👤 User : <code>{purchase['user_id']}</code>\n"
                f"💰 Harga : Rp {price:,}\n"
            ).replace(",", "."),
            parse_mode="HTML"
        )
    except Exception:
        logger.exception(
            "CHANNEL NOTIFY ERROR"
        )
    # =====================================================
    # OPEN FILE BUTTON
    # =====================================================
    try:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📂 OPEN FILE",
                        callback_data=(
                            f"page:{purchase['file_code']}:1"
                        )
                    )
                ]
            ]
        )
        await bot.send_message(
            purchase["user_id"],
            (
                "✅ <b>Pembayaran berhasil!</b>\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "📦 <b>File sudah tersedia</b>\n\n"
                "Klik tombol di bawah untuk membuka file.\n\n"
                "━━━━━━━━━━━━━━"
            ),
            parse_mode="HTML",
            reply_markup=kb
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
    # DUPLICATE PROTECTION
    # =====================================================
    if trx["status"] == "paid":
        logger.info(
            "VIP PAYMENT ALREADY PAID | invoice=%s",
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
            vip_until
        FROM users
        WHERE telegram_id=$1
        """,
        trx["user_id"]
    )
    now = datetime.now(
        timezone.utc
    )
    # =====================================================
    # CALCULATE VIP EXPIRATION
    # =====================================================
    if (
        user
        and user["vip_until"]
        and user["vip_until"] > now
    ):
        vip_until = (
            user["vip_until"]
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
            # Lock payment
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
                return {
                    "success": False,
                    "message": "Payment not found"
                }
            if locked_trx["status"] == "paid":
                return {
                    "success": True,
                    "message": "Already paid"
                }
            # ---------------------------------------------
            # Mark payment paid
            # ---------------------------------------------
            await conn.execute(
                """
                UPDATE payments
                SET status='paid'
                WHERE invoice_id=$1
                """,
                invoice_id
            )
            # ---------------------------------------------
            # Activate VIP
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
    logger.info(
        "VIP PAYMENT SUCCESS | invoice=%s payment_id=%s user=%s",
        invoice_id,
        payment_id,
        trx["user_id"]
    )
    # =====================================================
    # DELETE REDIS INVOICE
    # =====================================================
    await redis_client.delete(
        f"invoice:{invoice_id}"
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
                f"👤 User : <code>{trx['user_id']}</code>\n"
                f"📦 Paket : {paket['name']}"
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
