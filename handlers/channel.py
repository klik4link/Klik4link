from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.callback_query(F.data == "list_channel")
async def list_channel(call: CallbackQuery):

    text = (
        "📢 <b>GGBOT CHANNEL CENTER</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>Informasi Channel</b>\n\n"
        "Silakan bergabung ke channel resmi GGBOT "
        "untuk mendapatkan update terbaru, informasi sistem, "
        "dan pemberitahuan penting.\n\n"

        "⚠️ <b>Catatan:</b>\n"
        "• Wajib mengikuti channel update.\n"
        "• Informasi maintenance akan diumumkan melalui channel.\n"
        "• Jika bot mengalami gangguan atau terkena masalah, "
        "notifikasi akan dikirim melalui channel khusus.\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "📢 <b>Update Channel</b>\n"
        "Update fitur, berita, dan perkembangan bot.\n\n"

        "💳 <b>Transaksi Channel</b>\n"
        "Informasi pembayaran dan transaksi.\n\n"

        "🚨 <b>Notifikasi System</b>\n"
        "Pemberitahuan bot error, banned, atau gangguan sistem.\n\n"

        "💾 <b>Backup Channel</b>\n"
        "Channel cadangan jika terjadi masalah."
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📢 Update Channel",
                    url="https://t.me/+0sgsiLx3KONjODA0"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📢 Update Channel 2",
                    url="https://t.me/+BTYmULtD_0RiYzk5"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💳 Transaksi",
                    url="https://t.me/+NrHk5eHAiTFiNzc1"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🚨 Notifikasi System",
                    url="https://t.me/+iG0rS6GFY3Y2NTNk"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💾 Backup Channel",
                    url="https://t.me/+z7I7rz4TE2ozODBl"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Kembali",
                    callback_data="home"
                )
            ]

        ]
    )


    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await call.answer()
