from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def home_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📤 Upload Media",
                    callback_data="upfile"
                ),
                InlineKeyboardButton(
                    text="📥 Get Media",
                    callback_data="getfile"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👤 Account",
                    callback_data="account"
                ),
                InlineKeyboardButton(
                    text="💎 VIP",
                    callback_data="vip"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📢 List Channel",
                    callback_data="list_channel"
                ),
                InlineKeyboardButton(
                    text="ℹ️ Help",
                    callback_data="help"
                )
            ]

        ]
    )
