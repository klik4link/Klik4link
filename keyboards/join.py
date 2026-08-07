from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def join_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📢 Channel Update",
                    url="https://t.me/+0sgsiLx3KONjODA0"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📢 Channel Update 2",
                    url="https://t.me/+BTYmULtD_0RiYzk5"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💳 Channel Transaksi",
                    url="https://t.me/+NrHk5eHAiTFiNzc1"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⚠️ Notifikasi Bot",
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
                    text="✅ CHECK JOIN",
                    callback_data="check_sub"
                )
            ]

        ]
    )
