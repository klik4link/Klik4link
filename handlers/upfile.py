import asyncio
import json
import random
import string
import time

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CHANNEL_ID, BOT_USERNAME
from database import get_pool
from utils.force_sub import check_force_sub
from keyboards.join import join_kb

router = Router()

# =========================
# CONFIG
# =========================
MAX_MEDIA = 200
UPDATE_DELAY = 0.3

_last_update = {}
_user_locks = {}

def get_lock(user_id: int):
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]


# =========================
# SAFE EDIT
# =========================
async def safe_update(bot, chat_id, message_id, text, user_id, reply_markup=None):
    if not message_id:
        return

    now = time.time()
    last = _last_update.get(user_id, 0)

    if now - last < UPDATE_DELAY:
        await asyncio.sleep(UPDATE_DELAY)

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
        _last_update[user_id] = time.time()

    except TelegramBadRequest:
        pass


# =========================
# STATE
# =========================
class UploadState(StatesGroup):
    upload = State()
    wait_title = State()
    wait_category = State()
    wait_folder = State()
    wait_expiry = State()
    wait_price = State()


# =========================
# START UPLOAD
# =========================
@router.callback_query(F.data == "upfile")
async def start_upfile(call: CallbackQuery, state: FSMContext):

    await call.answer()

    async with get_lock(call.from_user.id):

        await state.clear()
        await state.set_state(UploadState.upload)

        if not await check_force_sub(call.bot, call.from_user.id):
            return await call.message.answer(
                "❌ Join channel terlebih dahulu.",
                reply_markup=join_kb()
            )

        msg = await call.message.edit_text("⏳ Loading...")
        await asyncio.sleep(0.2)

        await msg.edit_text(
            "📦 <b>UPLOAD MODE ACTIVE</b>\n\n"
            "📤 Kirim foto, video atau dokumen.\n"
            "Maksimal <b>200 file</b>.\n\n"
            "Jika sudah selesai tekan tombol <b>STOP & SAVE</b>.",
            parse_mode="HTML"
        )

        await state.update_data(
            upload_mode=True,

            # Media
            media=[],

            # Informasi File
            title=None,
            category=None,
            folder_name=None,

            # Share
            share_media=True,

            # Expired
            expiry=0,

            # Paid / Free
            is_paid=False,
            price=0,
            payment_provider=None,

            # Counter
            view_count=0,
            download_count=0,
            favorite_count=0,

            # Progress
            progress_msg_id=msg.message_id,
            saving=False
        )


# =========================
# RECEIVE MEDIA
# =========================
@router.message(F.document | F.video | F.photo)
async def receive_media(message: Message, state: FSMContext):

    async with get_lock(message.from_user.id):

        data = await state.get_data()

        if not data.get("upload_mode"):
            return

        media = data.get("media", [])

        if len(media) >= MAX_MEDIA:
            return await message.answer(
                f"❌ Maksimal {MAX_MEDIA} file."
            )

        # =========================
        # GET FILE INFO
        # =========================
        if message.document:
            file = message.document
            file_id = file.file_id
            file_name = file.file_name
            file_size = file.file_size
            media_type = "document"

        elif message.video:
            file = message.video
            file_id = file.file_id
            file_name = getattr(file, "file_name", None)
            file_size = file.file_size
            media_type = "video"

        else:
            file = message.photo[-1]
            file_id = file.file_id
            file_name = None
            file_size = file.file_size
            media_type = "photo"

        # =========================
        # DUPLICATE CHECK
        # =========================
        if any(x["file_id"] == file_id for x in media):
            return

        # =========================
        # SAVE TO MEMORY
        # =========================
        media.append(
            {
                "file_id": file_id,
                "type": media_type,
                "file_name": file_name,
                "file_size": file_size
            }
        )

        await state.update_data(media=media)

        # =========================
        # DELETE USER MESSAGE
        # =========================
        try:
            await message.delete()
        except Exception:
            pass

        # =========================
        # PROGRESS
        # =========================
        total = len(media)

        percent = int((total / MAX_MEDIA) * 100)

        progress = min(
            10,
            int(total / MAX_MEDIA * 10)
        )

        bar = (
            "█" * progress +
            "░" * (10 - progress)
        )

        text = (
            "📦 <b>UPLOAD MANAGER</b>\n\n"
            f"📁 Total File : <b>{total}</b>\n"
            f"📊 Progress : [{bar}] {percent}%\n"
            f"📥 Maksimal : {MAX_MEDIA}\n\n"
            "Jika semua file sudah terkirim,\n"
            "tekan tombol <b>STOP & SAVE</b>."
        )

        kb = InlineKeyboardBuilder()

        kb.button(
            text="⏹ STOP & SAVE",
            callback_data="save_upfile"
        )

        kb.button(
            text="❌ CANCEL",
            callback_data="cancel_upfile"
        )

        kb.adjust(2)

        await safe_update(
            message.bot,
            message.chat.id,
            data.get("progress_msg_id"),
            text,
            message.from_user.id,
            kb.as_markup()
        )


# =========================
# CANCEL
# =========================
@router.callback_query(F.data == "cancel_upfile")
async def cancel(call: CallbackQuery, state: FSMContext):

    await call.answer()

    data = await state.get_data()
    msg_id = data.get("progress_msg_id")

    await state.clear()

    try:
        if msg_id:
            await call.bot.delete_message(
                call.message.chat.id,
                msg_id
            )
    except Exception:
        pass

    await call.message.edit_text(
        "❌ <b>UPLOAD DIBATALKAN</b>",
        parse_mode="HTML"
    )


# =========================
# SAVE → SHARE MODE
# =========================
@router.callback_query(F.data == "save_upfile")
async def choose_share(call: CallbackQuery, state: FSMContext):

    await call.answer()

    data = await state.get_data()

    if data.get("saving"):
        return await call.answer(
            "Sedang diproses...",
            show_alert=True
        )

    if not data.get("media"):
        return await call.answer(
            "Belum ada file.",
            show_alert=True
        )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🔗 SHARE MEDIA",
        callback_data="share_yes"
    )

    kb.button(
        text="🔒 PRIVATE",
        callback_data="share_no"
    )

    kb.adjust(2)

    await call.message.edit_text(
        "📦 <b>PILIH MODE FILE</b>\n\n"
        "🔗 Share Media = File dapat dibagikan.\n"
        "🔒 Private = Hanya melalui kode.",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )


# =========================
# INPUT TITLE
# =========================
@router.message(UploadState.wait_title)
async def input_title(message: Message, state: FSMContext):

    title = (message.text or "").strip()

    if title.lower() == "/skip":
        title = "Untitled"

    if len(title) < 3:
        return await message.answer(
            "❌ Judul minimal 3 karakter."
        )

    await state.update_data(
        title=title
    )

    await state.set_state(
        UploadState.wait_category
    )

    await message.answer(
        "📂 Masukkan kategori file.\n\n"
        "Contoh:\n"
        "• Anime\n"
        "• Film\n"
        "Ketik /skip untuk kategori 'Lainnya'."
    )

# =========================
# SHARE HANDLER → FOLDER NAME
# =========================
# =========================
# SHARE HANDLER
# =========================
@router.callback_query(F.data.startswith("share_"))
async def handle_share(call: CallbackQuery, state: FSMContext):

    await call.answer()

    share_media = call.data == "share_yes"

    await state.update_data(
        share_media=share_media,
        saving=False
    )

    await state.set_state(UploadState.wait_title)

    await call.message.edit_text(
        "📝 <b>Masukkan Judul File</b>\n\n"
        "Contoh:\n"
        "<code>Video Saya</code>\n\n"
        "Ketik <code>/skip</code> untuk menggunakan judul otomatis.",
        parse_mode="HTML"
    )


# =========================
# INPUT CATEGORY
# =========================
@router.message(UploadState.wait_category)
async def input_category(message: Message, state: FSMContext):

    category = (message.text or "").strip()

    if category.lower() == "/skip":
        category = "Lainnya"

    await state.update_data(category=category)

    await state.set_state(UploadState.wait_folder)

    await message.answer(
        "📁 Masukkan nama folder.\n\n"
        "Ketik /skip untuk nama otomatis."
    )


# =========================
# INPUT FOLDER
# =========================
@router.message(UploadState.wait_folder)
async def input_folder(message: Message, state: FSMContext):

    text = (message.text or "").strip()

    if text.lower() == "/skip":
        folder_name = "Folder " + "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )
    else:
        folder_name = text[:50]

    await state.update_data(folder_name=folder_name)

    kb = InlineKeyboardBuilder()

    kb.button(text="⏳ 1 Jam", callback_data="exp:3600")
    kb.button(text="⏳ 24 Jam", callback_data="exp:86400")
    kb.button(text="♾ Permanent", callback_data="exp:0")

    kb.adjust(1)

    await message.answer(
        "🕒 Pilih waktu kadaluarsa file:",
        reply_markup=kb.as_markup()
    )

    await state.set_state(UploadState.wait_expiry)


# =========================
# EXPIRY
# =========================
@router.callback_query(F.data.startswith("exp:"))
async def set_expiry(call: CallbackQuery, state: FSMContext):

    await call.answer()

    expiry = int(call.data.split(":")[1])

    await state.update_data(expiry=expiry)

    kb = InlineKeyboardBuilder()

    kb.button(text="🆓 Free", callback_data="file_free")
    kb.button(text="💰 Paid", callback_data="file_paid")

    kb.adjust(2)

    await call.message.edit_text(
        "💎 Pilih tipe file:",
        reply_markup=kb.as_markup()
    )


# =========================
# FILE PAID
# =========================
@router.callback_query(F.data == "file_paid")
async def file_paid(call: CallbackQuery, state: FSMContext):

    await call.answer()

    await call.message.edit_text(
        "💰 Masukkan harga file.\n\n"
        "Minimal Rp1.000"
    )

    await state.set_state(UploadState.wait_price)


# =========================
# FILE FREE
# =========================
@router.callback_query(F.data == "file_free")
async def file_free(call: CallbackQuery, state: FSMContext):

    await call.answer()

    await state.update_data(
        is_paid=False,
        price=0,
        payment_provider=None
    )

    await call.message.edit_text("⏳ Menyimpan file...")

    await finalize_save(call.message, state)


# =========================
# INPUT PRICE
# =========================
@router.message(UploadState.wait_price)
async def input_price(message: Message, state: FSMContext):

    if not message.text or not message.text.isdigit():
        return await message.answer(
            "❌ Harga harus berupa angka."
        )

    price = int(message.text)

    if price < 1000:
        return await message.answer(
            "❌ Minimal harga Rp1.000."
        )

    await state.update_data(
        is_paid=True,
        price=price,
        payment_provider="bayargg"
    )

    await message.answer(
        "⏳ Menyimpan file..."
    )

    await finalize_save(message, state)
# =========================
# FINAL SAVE
# =========================
async def finalize_save(message: Message, state: FSMContext):

    async with get_lock(message.from_user.id):

        data = await state.get_data()

        media = data.get("media", [])

        if not media:
            return await message.answer(
                "❌ No media found"
            )


        # =========================
        # FILE INFO
        # =========================

        folder_name = data.get("folder_name") or "Folder AUTO"
        title = data.get("title") or folder_name
        category = data.get("category") or "General"

        creator = message.from_user.full_name


        # =========================
        # SETTINGS
        # =========================

        share_media = data.get(
            "share_media",
            True
        )

        expiry = data.get(
            "expiry",
            0
        )

        is_paid = data.get(
            "is_paid",
            False
        )

        price = data.get(
            "price",
            0
        )

        payment_provider = data.get(
            "payment_provider"
        )


        expires_at = None

        if expiry > 0:
            expires_at = int(time.time()) + expiry


        pool = await get_pool()


        user_id = int(
            message.from_user.id
        )


        # =========================
        # REGISTER USER / SELLER
        # =========================

        await pool.execute(
            """
            INSERT INTO users
            (
                telegram_id,
                username,
                fullname,
                first_name,
                chat_id
            )
            VALUES
            (
                $1::bigint,
                $2,
                $3,
                $4,
                $5::bigint
            )

            ON CONFLICT (telegram_id)
            DO UPDATE SET

                username = EXCLUDED.username,
                fullname = EXCLUDED.fullname,
                first_name = EXCLUDED.first_name,
                chat_id = EXCLUDED.chat_id

            """,

            user_id,
            message.from_user.username,
            message.from_user.full_name,
            message.from_user.first_name,
            user_id
        )


        # =========================
        # GENERATE CODE
        # =========================

        while True:

            video_count = sum(
                1 for x in media
                if x["type"] == "video"
            )

            photo_count = sum(
                1 for x in media
                if x["type"] == "photo"
            )

            document_count = sum(
                1 for x in media
                if x["type"] == "document"
            )


            random_code = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=8
                )
            )


            code = (
                f"GGB-"
                f"{video_count}V-"
                f"{photo_count}P-"
                f"{document_count}D-"
                f"{random_code}"
            )


            exists = await pool.fetchval(
                """
                SELECT 1
                FROM files
                WHERE code=$1
                """,
                code
            )


            if not exists:
                break

        # =========================
        # SAVE FILE
        # =========================

        await pool.execute(
            """
            INSERT INTO files
            (
                code,
                title,
                creator,
                category,
                folder_name,

                media,

                share_media,
                is_share,

                owner_id,
                seller_id,

                media_count,

                expires_at,

                is_paid,
                price,
                payment_provider,

                view_count,
                download_count,
                favorite_count
            )


            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,

                $6,

                $7,
                $8,

                $9::bigint,
                $10::bigint,

                $11,

                $12,

                $13,
                $14,
                $15,

                $16,
                $17,
                $18
            )

            """,

            code,
            title,
            creator,
            category,
            folder_name,

            json.dumps(media),

            share_media,
            share_media,

            user_id,
            user_id,

            len(media),

            expires_at,

            is_paid,
            price,
            payment_provider,

            0,
            0,
            0
        )


        await state.clear()



        # =========================
        # RESULT MESSAGE
        # =========================

        if is_paid:

            media_mode = (
                "💰 Media Mode : Paid\n"
                f"💵 Harga : Rp {price:,}"
                .replace(",", ".")
            )

        else:

            media_mode = (
                "🆓 Media Mode : Free"
            )



        text = (

            "✅ <b>FILE SAVED SUCCESSFULLY</b>\n\n"

            f"📝 Title : {title}\n"
            f"📋 Files : {len(media)}\n\n"
            f"🔑 Code :\n"
            f"<code>{code}</code>\n\n"
            f"{media_mode}\n\n"
            f"🤖 Bot : @{BOT_USERNAME}\n\n"

            "🔐 Kirim code tersebut ke bot untuk membuka file."

        )


        await message.answer(
            text,
            parse_mode="HTML"
        )


        # =========================
        # LOG CHANNEL
        # =========================

        try:

            me = await message.bot.get_me()

            await message.bot.send_message(
                CHANNEL_ID,
                text,
                parse_mode="HTML"
            )


        except Exception as e:

            print(
                "CHANNEL LOG ERROR:",
                e
            )
