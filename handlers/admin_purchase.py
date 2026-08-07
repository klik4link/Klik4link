from config import ADMIN_IDS


async def notify_admin_purchase(
    bot,
    user_id,
    code,
    price
):

    text = (
        "🔔 <b>PEMBELIAN BARU</b>\n\n"
        f"👤 User ID : <code>{user_id}</code>\n"
        f"📂 File : <code>{code}</code>\n"
        f"💰 Harga : Rp {price:,}"
    ).replace(",", ".")


    for admin_id in ADMIN_IDS:

        try:
            await bot.send_message(
                admin_id,
                text,
                parse_mode="HTML"
            )

        except Exception:
            pass
