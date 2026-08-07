import re

from aiogram import Router
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext


router = Router()


# =========================
# KEYBOARDS
# =========================

def getfile_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Get Media",
                    callback_data="getfile"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home"
                )
            ]
        ]
    )


def home_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Help",
                    callback_data="help"
                )
            ]
        ]
    )


# =========================
# GLOBAL USER GUIDE
# =========================

@router.message()
async def notify_user(
    message: Message,
    state: FSMContext
):

    # Jangan ganggu fitur aktif
    if await state.get_state():
        return


    # =========================
    # MEDIA DETECT
    # =========================

    if (
        message.video
        or message.photo
        or message.document
        or message.audio
        or message.animation
        or message.voice
    ):

        return await message.reply(
            "📤 <b>Upload Media</b>\n\n"
            "Media terdeteksi.\n\n"
            "Untuk upload file silakan tekan menu:\n"
            "📤 <b>Upload Media</b>\n\n"
            "Bot akan membuat kode file otomatis.",
            reply_markup=home_kb()
        )


    # =========================
    # TEXT CHECK
    # =========================

    if not message.text:
        return


    text = message.text.strip()


    # =========================
    # GGB CODE DETECT
    # =========================

    if re.search(
        r"GGB-[A-Za-z0-9-]+",
        text,
        re.IGNORECASE
    ):

        return await message.reply(
            "📥 <b>Get Media</b>\n\n"
            "Kode file terdeteksi.\n\n"
            "Tekan tombol di bawah untuk membuka file.",
            reply_markup=getfile_kb()
        )


    # =========================
    # OLD LINK DETECT
    # =========================

    if "start=getfile_" in text.lower():

        return await message.reply(
            "📥 <b>Get Media</b>\n\n"
            "Link file terdeteksi.\n\n"
            "Tekan tombol Get Media untuk mengambil file.",
            reply_markup=getfile_kb()
        )


    # =========================
    # DEFAULT MESSAGE
    # =========================

    await message.reply(
        "🤖 <b>GGBOT</b>\n\n"
        "Saya belum memahami pesan tersebut.\n\n"
        "Silakan gunakan menu:\n\n"

        "📤 <b>Upload Media</b>\n"
        "Upload video, foto, atau dokumen.\n\n"

        "📥 <b>Get Media</b>\n"
        "Ambil file menggunakan kode.\n\n"

        "👤 <b>Account</b>\n"
        "Kelola akun dan saldo.\n\n"

        "💎 <b>VIP</b>\n"
        "Upgrade fitur premium.\n\n"

        "ℹ️ <b>Help</b>\n"
        "Panduan penggunaan bot.",

        reply_markup=home_kb()
    )
