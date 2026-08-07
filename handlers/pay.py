import qrcode
import logging
from config import QR_PAYMENT
from io import BytesIO

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile
)

from database import fetchrow, execute
from utils.bayaron import BayarOn
from utils.redis_client import safe_set, safe_delete
from handlers.admin_purchase import notify_admin_purchase


logger = logging.getLogger(__name__)

router = Router()


PAY_LOCK_TTL = 30
INVOICE_TTL = 3600


# =================================================
# MENU PEMBAYARAN
# =================================================

@router.callback_query(F.data.startswith("pay:"))
async def pay_menu(call: CallbackQuery):

    code = call.data.split(":")[1]


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



# =================================================
# BAYAR OTOMATIS BAYARON
# =================================================

@router.callback_query(F.data.startswith("auto_pay:"))
async def auto_pay(call: CallbackQuery):

    await call.answer(
        "⏳ Membuat pembayaran..."
    )


    user_id = call.from_user.id

    code = call.data.split(":")[1]


    loading = await call.message.answer(
        "⏳ <b>Membuat QRIS otomatis...</b>",
        parse_mode="HTML"
    )


    lock_key = f"paylock:{user_id}:{code}"


    try:

        lock = await safe_set(
            lock_key,
            "1",
            ex=PAY_LOCK_TTL,
            nx=True
        )


    except:

        lock = True



    if not lock:

        await loading.delete()

        return await call.answer(
            "Tunggu sebentar",
            show_alert=True
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
                "File tidak ditemukan",
                show_alert=True
            )


        if not file["is_paid"]:

            return await call.answer(
                "File gratis",
                show_alert=True
            )


        if file["owner_id"] == user_id:

            return await call.answer(
                "Owner tidak perlu bayar",
                show_alert=True
            )



        price = file["price"] or 0



        # =========================
        # CREATE BAYARON
        # =========================

        data = await BayarOn.create_payment(
            amount=price,
            description=f"File {code}",
            customer_name=call.from_user.full_name
        )


        if not data:

            return await call.answer(
                "Gagal membuat pembayaran",
                show_alert=True
            )



        transaction = data.get(
            "transaction",
            {}
        )


        invoice_id = transaction.get(
            "reference_id"
        )


        if not invoice_id:

            return await call.answer(
                "Invoice gagal",
                show_alert=True
            )


        amount = transaction.get(
            "amount_total",
            price
        )



        qris = await BayarOn.init_qris(
            invoice_id
        )


        qr_string = (
            qris.get("qr_code")
            or qris.get("qr_string")
            or qris.get("qr")
        )


        if not qr_string:

            return await call.answer(
                "QRIS gagal dibuat",
                show_alert=True
            )



        # =========================
        # SAVE DATABASE
        # =========================

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
                $1,$2,$3,$4,$5,
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



        await notify_admin_purchase(
            bot=call.bot,
            user_id=user_id,
            code=code,
            price=price
        )



        await safe_set(
            f"invoice:{invoice_id}",
            f"{user_id}:{code}:pending",
            ex=INVOICE_TTL
        )



        # =========================
        # BUAT QR IMAGE
        # =========================

        qr = qrcode.make(
            qr_string
        )


        buf = BytesIO()

        qr.save(
            buf,
            format="PNG"
        )

        buf.seek(0)



        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[

                [
                    InlineKeyboardButton(
                        text="✅ Check Payment",
                        callback_data=f"check:{invoice_id}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="❌ Cancel",
                        callback_data=f"cancel:{invoice_id}"
                    )
                ]

            ]
        )



        await call.message.delete()



        msg = await call.message.answer_photo(
            BufferedInputFile(
                buf.getvalue(),
                filename="qris.png"
            ),

            caption=(
                "⚡ <b>PAYMENT OTOMATIS</b>\n\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : Rp {amount:,}\n\n"
                "Scan QR dan bot akan cek otomatis."
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
            "AUTO PAY ERROR"
        )

        raise



    finally:

        try:
            await loading.delete()
        except:
            pass


        try:
            await safe_delete(
                lock_key
            )
        except:
            pass


# =================================================
# BAYAR MANUAL QR GOPAY MERCHANT
# =================================================

@router.callback_query(F.data.startswith("manual_pay:"))
async def manual_pay(call: CallbackQuery):

    await call.answer(
        "⏳ Menyiapkan pembayaran..."
    )


    user_id = call.from_user.id
    code = call.data.split(":")[1]


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
                "File tidak ditemukan",
                show_alert=True
            )


        if not file["is_paid"]:

            return await call.answer(
                "File gratis",
                show_alert=True
            )


        if file["owner_id"] == user_id:

            return await call.answer(
                "Owner tidak perlu bayar",
                show_alert=True
            )


        price = file["price"] or 0



        # =========================
        # CREATE MANUAL INVOICE
        # =========================

        import time

        invoice_id = (
            f"MANUAL-{user_id}-{code}-{int(time.time())}"
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
                $1,$2,$3,$4,$5,
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



        await notify_admin_purchase(
            bot=call.bot,
            user_id=user_id,
            code=code,
            price=price
        )

        await safe_set(
            f"invoice:{invoice_id}",
            f"{user_id}:{code}:pending",
            ex=INVOICE_TTL
        )



        # =========================
        # AMBIL QR GOPAY
        # =========================

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
                        callback_data=f"manual_check:{invoice_id}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="❌ Batal",
                        callback_data=f"cancel:{invoice_id}"
                    )
                ]

            ]
        )



        try:
            await call.message.delete()
        except:
            pass



        msg = await call.message.answer_photo(
            BufferedInputFile(
                buf.getvalue(),
                filename="gopay.png"
            ),

            caption=(
                "📲 <b>PEMBAYARAN MANUAL</b>\n\n"
                f"📂 File : <code>{code}</code>\n"
                f"💰 Nominal : <b>Rp {price:,}</b>\n\n"
                "📷 Silakan scan QR GoPay Merchant di atas.\n\n"
                "⚠️ <b>PENTING!</b>\n"
                "• Nominal pembayaran <b>WAJIB</b> sama persis dengan nominal yang tertera.\n"
                "• Pembayaran dengan nominal kurang atau lebih tidak dapat diverifikasi otomatis.\n"
                "• Setelah transfer berhasil, tekan tombol <b>✅ Saya Sudah Bayar</b>.\n"
                "• Admin akan memverifikasi pembayaran terlebih dahulu sebelum file dapat dibuka."
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
        except:
            pass
