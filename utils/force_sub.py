import logging

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
)


# =========================
# FORCE SUB CHANNEL
# =========================

FORCE_CHANNELS = [

    # Channel Update
    -1004449050731,

    # Channel Update 2
    -1003978483597,

    # Channel Transaksi
    -1003894841696,

]


# =========================
# CHECK FORCE SUB
# =========================

async def check_force_sub(
    bot: Bot,
    user_id: int
) -> bool:


    if not FORCE_CHANNELS:
        return True


    for channel_id in FORCE_CHANNELS:

        try:

            member = await bot.get_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )


            if member.status not in (
                "member",
                "administrator",
                "creator"
            ):

                return False


        except (
            TelegramBadRequest,
            TelegramForbiddenError
        ) as e:

            logging.error(
                "FORCE SUB ERROR | Channel=%s User=%s Error=%s",
                channel_id,
                user_id,
                e
            )

            return False


        except Exception:

            logging.exception(
                "FORCE SUB UNKNOWN ERROR"
            )

            return False


    return True
