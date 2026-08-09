import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.force_sub import check_force_sub
from keyboards.menu import home_kb
from keyboards.join import join_kb
from database import get_pool
router = Router()
# =========================
# START
# =========================
@router.message(CommandStart())
async def start_cmd(
    message: Message,
    state: FSMContext
):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    try:
        pool = await get_pool()
        # =========================
        # REGISTER / UPDATE USER
        # =========================
        await pool.execute(
            """
            INSERT INTO users
            (
                telegram_id,
                username,
                chat_id,
                balance
            )
            VALUES
            ($1, $2, $3, 0)
            ON CONFLICT (telegram_id)
            DO UPDATE SET
                username = EXCLUDED.username,
                chat_id = EXCLUDED.chat_id
            """,
            user_id,
            username,
            message.chat.id
        )
        # =========================
        # LOADING
        # =========================
        loading = await message.answer(
            "🤖 <b>𝗚𝗚𝗕𝗢𝗧</b>\n"
            "<i>Loading...</i>",
            parse_mode="HTML"
        )
        await process_start(
            message,
            loading,
            user_id,
            username
        )
    except Exception:
        logging.exception("START ERROR")
        await message.answer(
            "❌ <b>System Error</b>",
            parse_mode="HTML"
        )
# =========================
# PROCESS START
# =========================
async def process_start(
    message,
    loading,
    user_id,
    username
):
    # =========================
    # FORCE SUB
    # =========================
    try:
        sub = await check_force_sub(
            message.bot,
            user_id
        )
    except Exception:
        sub = True
    if not sub:
        return await loading.edit_text(
            "📢 <b>𝗝𝗼𝗶𝗻 𝗗𝗶𝗽𝗲𝗿𝗹𝘂𝗸𝗮𝗻</b>\n\n"
            "Silakan bergabung ke semua channel terlebih dahulu.",
            parse_mode="HTML",
            reply_markup=join_kb()
        )
    # =========================
    # LOAD USER
    # =========================
    pool = await get_pool()
    user = await pool.fetchrow(
        """
        SELECT
            username,
            vip,
            vip_until
        FROM users
        WHERE telegram_id=$1
        """,
        user_id
    )
    if not user:
        return await loading.edit_text(
            "❌ <b>User tidak ditemukan.</b>",
            parse_mode="HTML"
        )
    # =========================
    # HOME
    # =========================
    await render_home_fast(
        message.bot,
        loading,
        user_id,
        user["username"] or username,
        user["vip"],
        user["vip_until"]
    )
# =========================
# HOME UI
# =========================
async def render_home_fast(
    bot,
    message,
    user_id,
    username,
    vip,
    vip_until
):
    # =========================
    # CHECK VIP ACTIVE
    # =========================
    is_vip_active = (
        vip is True
        and vip_until is not None
        and vip_until > datetime.now()
    )
    if is_vip_active:
        account_status = "💎 VIP"
    else:
        account_status = "🆓 FREE"
    # =========================
    # HOME TEXT
    # =========================
    text = (
        "🤖 <b>𝗚𝗚𝗕𝗢𝗧</b>\n"
        "<i>Smart File Sharing Platform</i>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <code>{user_id}</code>  |  "
        f"👤 @{username}  |  "
        f"{account_status}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "✨ <b>Selamat datang di GGBOT.</b>\n"
        "Silakan pilih menu yang tersedia di bawah."
    )
    # =========================
    # UPDATE HOME
    # =========================
    try:
        await message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=home_kb()
        )
    except Exception:
        await bot.send_message(
            user_id,
            text,
            parse_mode="HTML",
            reply_markup=home_kb()
        )
# =========================
# CALLBACK HOME
# =========================
@router.callback_query(F.data == "home")
async def back_home(
    call: CallbackQuery,
    state: FSMContext
):
    await call.answer()
    await state.clear()
    user_id = call.from_user.id
    # =========================
    # FORCE SUB
    # =========================
    try:
        ok = await check_force_sub(
            call.bot,
            user_id
        )
    except Exception:
        ok = True
    if not ok:
        return await call.message.answer(
            "📢 <b>𝗝𝗼𝗶𝗻 𝗗𝗶𝗽𝗲𝗿𝗹𝘂𝗸𝗮𝗻</b>\n\n"
            "Silakan bergabung ke semua channel terlebih dahulu.",
            parse_mode="HTML",
            reply_markup=join_kb()
        )
    # =========================
    # LOAD USER
    # =========================
    pool = await get_pool()
    user = await pool.fetchrow(
        """
        SELECT
            username,
            vip,
            vip_until
        FROM users
        WHERE telegram_id=$1
        """,
        user_id
    )
    if not user:
        return await call.message.edit_text(
            "❌ <b>User tidak ditemukan.</b>",
            parse_mode="HTML"
        )
    # =========================
    # RENDER HOME
    # =========================
    await render_home_fast(
        call.bot,
        call.message,
        user_id,
        user["username"] or "unknown",
        user["vip"],
        user["vip_until"]
    )
