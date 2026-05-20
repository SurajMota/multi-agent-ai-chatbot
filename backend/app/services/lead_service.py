# backend/app/services/lead_service.py

from server.logger import log
from datetime import datetime


class LeadService:
    """
    Lead Service (SAFE MODE)

    ✔ Does NOT touch Unanswered_Questions sheet
    ✔ Ready for Make / Webhook / DB later
    ✔ Never crashes chat
    """

    def __init__(self):
        log.info("🗂 LeadService initialized (SAFE MODE)")

    # ------------------------------------------------------------------
    # SAVE LEAD
    # ------------------------------------------------------------------
    async def save_lead(self, name="", email="", phone="", program="", transcript=None):
        timestamp = datetime.utcnow().isoformat()

        transcript_text = ""
        if transcript:
            transcript_text = "\n".join(
                [f"{m['time']} | {m['role']}: {m['msg']}" for m in transcript]
            )

        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "program": program,
            "timestamp": timestamp,
            "transcript": transcript_text,
        }

        # 🔹 LOG ONLY (no Sheets)
        log.info(f"[LEAD] {payload}")

        return {"success": True}
