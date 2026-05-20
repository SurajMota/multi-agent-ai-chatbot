# backend/app/services/unanswered_logger.py

from datetime import datetime
from app.tools.google_sheets import GoogleSheetClient
from server.logger import log


# ---------------------------------------------------
# Fallback phrases = NOT real answers
# ---------------------------------------------------
FALLBACK_PHRASES = [
    "i don't have that information",
    "i do not have that information",
    "i'm not sure",
    "i am not sure",
    "i couldn't find",
    "i could not find",
    "no information available",
]


def is_fallback_response(text: str) -> bool:
    if not text:
        return True
    text = text.lower().strip()
    return any(p in text for p in FALLBACK_PHRASES)


class UnansweredLogger:
    """
    Logs ONLY true unanswered knowledge questions.

    ✔ One row per question
    ✔ No duplicates per session
    ✔ No empty questions
    ✔ Google Sheets safe
    """

    def __init__(self):
        self.gs = GoogleSheetClient()
        self.logged_cache = set()

    async def log(
        self,
        session_id: str,
        question: str,
        intent: str,
        language: str,
        source: str = "kb_fallback",
    ):
        if not question or not question.strip():
            log.warning("⚠ Empty question — skipping unanswered logging")
            return

        key = f"{session_id}:{question.lower().strip()}"
        if key in self.logged_cache:
            return

        self.logged_cache.add(key)

        try:
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "question": question.strip(),
                "intent": intent,
                "language": language,
                "rag_used": False,
                "source": source,
                "resolved": False,
                "notes": "",
            }

            await self.gs.append_row(row)
            log.info("📝 Unanswered question logged")

        except Exception:
            log.exception("❌ Unanswered question logging failed")
