# backend/app/core/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # --- API KEYS ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")

    # --- GOOGLE SHEETS ---
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SERVICE_ACCOUNT_JSON_PATH: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", "./credentials.json")

    # --- MAKE.COM WEBHOOK ---
    MAKE_WEBHOOK_URL: str = os.getenv("MAKE_WEBHOOK_URL", "")

    # --- MODEL CONFIG ---
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "openai")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")

    # --- DEFAULT BOT APPEARANCE ---
    DEFAULT_BOT_NAME: str = os.getenv("DEFAULT_BOT_NAME", "AI Student Assistant")
    DEFAULT_BRAND_COLOR: str = os.getenv("DEFAULT_BRAND_COLOR", "#0A84FF")

    # --- CACHE ---
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", 2592000))  # 30 days

    # --- SERVER CONFIG ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # --- CLIENT PORTAL CONFIGURATION ---
# =====================================================

    # 🔹 Toggle this per client
    CLIENT_PORTAL_ENABLED: bool = os.getenv("CLIENT_PORTAL_ENABLED","False" ).lower() == "true" 
    CLIENT_PORTAL_URL: str = os.getenv("CLIENT_PORTAL_URL", "")
    CLIENT_PORTAL_AUTH: str = os.getenv("CLIENT_PORTAL_AUTH", "")
    CLIENT_PORTAL_USERNAME: str = os.getenv("CLIENT_PORTAL_USERNAME", "")
    CLIENT_PORTAL_PASSWORD: str = os.getenv("CLIENT_PORTAL_PASSWORD", "")

settings = Settings()
