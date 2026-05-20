# backend/app/tools/google_sheets.py

from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from app.config import settings
from server.logger import log


class GoogleSheetClient:
    """
    Google Sheets client for UNANSWERED QUESTIONS ONLY
    """

    def __init__(self):
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]

            json_path = os.path.abspath(settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH)
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"Credentials file not found: {json_path}")

            creds = Credentials.from_service_account_file(json_path, scopes=scopes)
            self.client = gspread.authorize(creds)

            spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            self.sheet = spreadsheet.worksheet("Unanswered_Questions")

            log.info("✅ Google Sheets (Unanswered_Questions) initialized")

        except Exception:
            log.exception("❌ Google Sheets init failed")
            self.sheet = None

    async def append_row(self, data: dict):
        """
        Append ONLY unanswered questions.
        """

        if not self.sheet:
            return False

        question = (data.get("question") or "").strip()
        if not question:
            log.warning("⚠ Empty question — skipping Google Sheets write")
            return False

        row = [
            data.get("timestamp", datetime.utcnow().isoformat()),
            data.get("session_id"),
            question,
            data.get("intent"),
            data.get("language"),
            data.get("rag_used", False),
            data.get("source", "fallback"),
            data.get("resolved", False),
            data.get("notes"),
        ]

        try:
            self.sheet.append_row(row, value_input_option="RAW")
            log.info("✅ Unanswered question saved to Google Sheets")
            return True
        except Exception:
            log.exception("❌ Failed to append unanswered question")
            return False
