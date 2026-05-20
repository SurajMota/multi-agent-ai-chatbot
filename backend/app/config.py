# backend/app/config.py

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    # =======================================
    # 🔑 OpenAI / LLM
    # =======================================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

    # =======================================
    # 🧠 Pinecone (RAG)
    # =======================================
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV = os.getenv("PINECONE_ENV", "")

    # =======================================
    # 📊 Google Sheets
    # (Used for Analytics + Unanswered Questions)
    # =======================================
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SERVICE_ACCOUNT_JSON_PATH = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON_PATH", ""
    )

    # =======================================
    # 🔗 Make.com Webhook (Optional)
    # =======================================
    MAKE_WEBHOOK_URL = os.getenv(
        "MAKE_WEBHOOK_URL",
        "https://hook.us1.make.com/ljvdqlnhycttwxziasd0j3617ofdaiws"
    )

    # =======================================
    # 🤖 Bot Defaults
    # =======================================
    DEFAULT_BOT_NAME = os.getenv(
        "DEFAULT_BOT_NAME", "AI Student Assistant"
    )
    BRAND_COLOR = os.getenv("DEFAULT_BRAND_COLOR", "#0A84FF")

    # =======================================
    # 🧠 Cache
    # =======================================
    CACHE_TTL_SECONDS = int(
        os.getenv("CACHE_TTL_SECONDS", "2592000")  # 30 days
    )

    # =======================================
    # 🌐 Server
    # =======================================
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # =======================================
    # 🌍 Translation (SAFE DEFAULTS)
    # =======================================
    # OFF by default → bot behavior unchanged
    TRANSLATION_ENABLED = os.getenv(
        "TRANSLATION_ENABLED", "false"
    ).lower() == "true"

    # Top 10 most-used global languages
    # Enable ONLY when client requests
    SUPPORTED_LANGUAGES = {
        "en": True,    # English (default)
        "es": False,   # Spanish
        "fr": False,   # French
        "de": False,   # German
        "pt": False,   # Portuguese
        "it": False,   # Italian
        "hi": False,   # Hindi
        "ar": False,   # Arabic
        "zh": False,   # Chinese
        "ru": False,   # Russian
    }


# Singleton settings object
settings = Settings()
