# backend/app/agents/translator_agent.py

from langdetect import detect, LangDetectException
from app.config import settings
from app.core.llm import llm_model
from server.logger import log


class TranslatorAgent:
    """
    🌍 Translator Agent (SAFE MIDDLEWARE)

    • OFF by default
    • Auto-detects user language (FREE)
    • Translates inbound → English (if enabled)
    • Translates outbound → user language (if enabled)
    • NEVER breaks existing flows
    """

    # Language code → readable name (LLM-friendly)
    LANGUAGE_NAMES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "pt": "Portuguese",
        "it": "Italian",
        "hi": "Hindi",
        "ar": "Arabic",
        "zh": "Chinese",
        "ru": "Russian",
    }

    def __init__(self):
        # SAFE DEFAULTS
        self.enabled = getattr(settings, "TRANSLATION_ENABLED", False)
        self.allowed_languages = getattr(
            settings, "SUPPORTED_LANGUAGES", {"en": True}
        )

        log.info(
            f"[TranslatorAgent] Enabled={self.enabled}, "
            f"Languages={self.allowed_languages}"
        )

    # --------------------------------------------------
    # 1️⃣ LANGUAGE DETECTION (NO LLM → FREE)
    # --------------------------------------------------
    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            return lang if lang in self.allowed_languages else "en"
        except LangDetectException:
            return "en"
        except Exception:
            log.exception("Language detection failed")
            return "en"

    # --------------------------------------------------
    # 2️⃣ CHECK IF TRANSLATION SHOULD RUN
    # --------------------------------------------------
    def should_translate(self, lang: str) -> bool:
        return (
            self.enabled
            and lang != "en"
            and self.allowed_languages.get(lang, False)
        )

    # --------------------------------------------------
    # 3️⃣ USER → ENGLISH
    # --------------------------------------------------
    async def to_english(self, text: str, lang: str) -> str:
        if not self.should_translate(lang):
            return text

        lang_name = self.LANGUAGE_NAMES.get(lang, lang)

        prompt = f"""
Translate the following text from {lang_name} to English.
Do NOT add, remove, or interpret anything.

Text:
{text}
"""

        try:
            reply = await llm_model().acomplete(prompt)
            return reply.strip() if reply else text
        except Exception:
            log.exception("Translator inbound failed")
            return text

    # --------------------------------------------------
    # 4️⃣ ENGLISH → USER LANGUAGE
    # --------------------------------------------------
    async def from_english(self, text: str, lang: str) -> str:
        if not self.should_translate(lang):
            return text

        lang_name = self.LANGUAGE_NAMES.get(lang, lang)

        prompt = f"""
Translate the following text from English to {lang_name}.
Do NOT add, remove, or interpret anything.

Text:
{text}
"""

        try:
            reply = await llm_model().acomplete(prompt)
            return reply.strip() if reply else text
        except Exception:
            log.exception("Translator outbound failed")
            return text
