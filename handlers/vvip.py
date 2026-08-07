from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# =========================
# USERNAME ADMIN VIP
# TANPA TANDA @
# Contoh:
# ADMIN_USERNAME = "adminvip"
# =========================
ADMIN_USERNAME = "ownergbot"


# =========================
# VIP MENU
# =========================
@router.callback_query(F.data == "vvip")
async def vvip_menu(call: CallbackQuery):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="💎 VIP 1 Hari • Rp20.000",
        url=(
            f"https://t.me/{ADMIN_USERNAME}"
            "?text=Halo%20Admin%20VIP,%20"
            "saya%20ingin%20membeli%20VIP%201%20Hari."
        )
    )

    kb.button(
        text="💎 VIP 3 Hari • Rp30.000",
        url=(
            f"https://t.me/{ADMIN_USERNAME}"
            "?text=Halo%20Admin%20VIP,%20"
            "saya%20ingin%20membeli%20VIP%203%20Hari."
        )
    )

    kb.button(
        text="💎 VIP 5 Hari • Rp40.000",
        url=(
            f"https://t.me/{ADMIN_USERNAME}"
            "?text=Halo%20Admin%20VIP,%20"
            "saya%20ingin%20membeli%20VIP%205%20Hari."
        )
    )

    kb.button(
        text="💎 VIP 7 Hari • Rp50.000",
        url=(
            f"https://t.me/{ADMIN_USERNAME}"
            "?text=Halo%20Admin%20VIP,%20"
            "saya%20ingin%20membeli%20VIP%207%20Hari."
        )
    )

    kb.button(
        text="🔙 Kembali",
        callback_data="account"
    )

    kb.adjust(1)

    text = (
        "💎 <b>PEMBELIAN VIP MANUAL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ <b>Pembelian VIP sementara diproses secara manual.</b>\n\n"

        "Server pembayaran otomatis sedang mengalami gangguan sehingga "
        "seluruh transaksi VIP akan dilayani langsung oleh <b>Admin VIP</b>.\n\n"

        "📌 <b>Cara Pembelian</b>\n"
        "1. Pilih paket VIP yang diinginkan.\n"
        "2. Anda akan diarahkan ke chat <b>Admin VIP</b>.\n"
        "3. Pesan akan terisi otomatis.\n"
        "4. Tekan tombol <b>Kirim</b>.\n"
        "5. Admin akan mengirimkan QRIS pembayaran.\n"
        "6. Lakukan pembayaran sesuai nominal paket.\n\n"

        "❗ <b>Catatan Penting</b>\n"
        "• Hubungi <b>Admin VIP</b>, bukan Admin Media.\n"
        "• Mohon <b>jangan spam</b> atau mengirim pesan berulang kali.\n"
        "• Admin sedang melayani banyak antrean VIP dan akan membalas sesuai urutan.\n"
        "• Setelah QRIS diterima, silakan scan dan bayar sesuai harga paket yang dipilih.\n\n"

        "Terima kasih atas pengertian dan kesabarannya. 🙏"
    )

    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

    await call.answer()
