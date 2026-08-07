from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

def language_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇮🇩 Bahasa Indonesia",
                    callback_data="lang:id"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇸 English",
                    callback_data="lang:en"
                )
            ]
        ]
    )
