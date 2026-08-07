from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def get_qr_id(message: Message):

    if message.photo:

        file_id = message.photo[-1].file_id

        await message.answer(
            f"ID QR kamu:\n\n<code>{file_id}</code>",
            parse_mode="HTML"
        )
