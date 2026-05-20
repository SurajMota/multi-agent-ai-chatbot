# backend/app/services/sheet_writer.py

from datetime import datetime
from app.tools.google_sheets import append_row
from server.logger import log   #removed it

class SheetWriter:

    async def save_appointment(self, payload: dict):
        """
        Save appointment details to Google Sheets.
        """

        try:
            row = [
                payload.get("name"),
                payload.get("email"),
                payload.get("phone"),
                payload.get("service"),
                payload.get("summary"),
                datetime.utcnow().isoformat(),
                "appointment"
            ]
            append_row(row)

            log.info("[APPOINTMENT SAVED] Data stored in Google Sheet.")

        except Exception as e:
            log.exception("Failed to write appointment to sheet", exc_info=e)
            return False

        return True
