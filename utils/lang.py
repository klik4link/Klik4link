# =========================
# LANGUAGE SYSTEM
# =========================

LANG = {

    "id": {

        "loading":
            "🤖 <b>𝗚𝗚𝗕𝗢𝗧</b>\n"
            "<i>Memuat...</i>",

        "join_required":
            "📢 <b>𝗝𝗼𝗶𝗻 𝗗𝗶𝗽𝗲𝗿𝗹𝘂𝗸𝗮𝗻</b>\n\n"
            "Silakan bergabung ke semua channel terlebih dahulu.",

        "welcome":
            "✨ <b>Selamat datang di GGBOT.</b>\n"
            "Silakan pilih menu yang tersedia di bawah."

    },


    "en": {

        "loading":
            "🤖 <b>𝗚𝗚𝗕𝗢𝗧</b>\n"
            "<i>Loading...</i>",

        "join_required":
            "📢 <b>Join Required</b>\n\n"
            "Please join all required channels first.",

        "welcome":
            "✨ <b>Welcome to GGBOT.</b>\n"
            "Please select a menu below."

    }

}



# =========================
# GET TEXT
# =========================

def get_text(lang, key):

    if lang not in LANG:
        lang = "id"

    return LANG[lang].get(
        key,
        LANG["id"].get(key, key)
    )
