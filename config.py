import os
from dotenv import load_dotenv
load_dotenv()
# =========================
# GENERAL
# =========================
TIMEZONE = "Asia/Jakarta"
# =========================
# BOT
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "Ggrobot"
BOT_URL = f"https://t.me/{BOT_USERNAME}"
# =========================
# DATABASE
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
# =========================
# PAYMENT
# =========================
# manual = QR GoPay Merchant + approve admin
# bayaron = pembayaran otomatis BayarOn
# dompetx = pembayaran otomatis DompetX
PAYMENT_MODE = os.getenv(
    "PAYMENT_MODE",
    "manual"
).lower().strip()
QR_PAYMENT = (
    "AgACAgUAAxkBAAKEv2p1r2DLEtZexB8c3zcoBn5pmffnAAILFGsb10WhV0rrpqQNiZuOAQADAgADeAADPQQ"
)
# -------------------------
# BAYARON
# -------------------------
BAYARON_API_KEY = os.getenv(
    "BAYARON_API_KEY"
)
BAYARON_MERCHANT = os.getenv(
    "BAYARON_MERCHANT"
)
BAYARON_WEBHOOK_SECRET = os.getenv(
    "BAYARON_WEBHOOK_SECRET"
)
# -------------------------
# DOMPETX
# -------------------------
DOMPETX_API_KEY = os.getenv(
    "DOMPETX_API_KEY"
)
# =========================
# CHANNEL / GROUP
# =========================
CHANNEL_ID = int(
    os.getenv(
        "CHANNEL_ID",
        "-1004449050731"
    )
)
# Channel khusus laporan penjualan
SALES_CHANNEL_ID = int(
    os.getenv(
        "SALES_CHANNEL_ID",
        "-1003894841696"
    )
)
GROUP_ID = int(
    os.getenv(
        "GROUP_ID",
        str(CHANNEL_ID)
    )
)
# =========================
# WITHDRAW
# =========================
WITHDRAW_CHANNEL_ID = int(
    os.getenv(
        "WITHDRAW_CHANNEL_ID",
        str(CHANNEL_ID)
    )
)
# =========================
# ADMIN
# =========================
ADMIN_IDS = [
    int(x)
    for x in os.getenv(
        "ADMIN_IDS",
        "6665664367"
    ).split(",")
    if x.strip().isdigit()
]
# =========================
# VALIDATION
# =========================
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN belum di-set di .env"
    )
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL belum di-set di .env"
    )
if (
    PAYMENT_MODE == "bayaron"
    and not BAYARON_API_KEY
):
    raise ValueError(
        "BAYARON_API_KEY belum di-set di .env / Railway Variables"
    )
if (
    PAYMENT_MODE == "dompetx"
    and not DOMPETX_API_KEY
):
    raise ValueError(
        "DOMPETX_API_KEY belum di-set di .env / Railway Variables"
    )
