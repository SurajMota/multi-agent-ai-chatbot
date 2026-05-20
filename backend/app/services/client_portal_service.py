import httpx
from datetime import datetime
from server.logger import log
from app.config import settings


class ClientPortalService:
    """
    Sends lead data to client portal (if enabled).
    Does NOT affect Make.com flow.
    """

    async def send_lead(self, lead: dict):

        # 🔒 If portal disabled → skip safely
        if not settings.CLIENT_PORTAL_ENABLED:
            log.info("Client portal disabled — skipping")
            return False

        if not settings.CLIENT_PORTAL_URL:
            log.warning("Client portal URL not configured")
            return False

        today_date = datetime.utcnow().strftime("%m/%d/%Y")

        # 🔹 Course Mapping (adjust per client if needed)
        course_id_map = {
            "Dialysis Technician": 1,
            "Diagnostic Medical Sonographer": 2,
            "Medical Assistant(RMA)": 3,
            "EKG Technician (Electrocardiography)": 4,
            "Phlebotomy Technician (Blood Draw Techniques)": 5,
            "EKG & Phlebotomy (CET & CPT)": 6,
            "Medical Billing (Computerized ICD10 & CPT Coding)": 7,
            "Medical Office Administration (CMAA)": 8,
            "Patient Care Technician(PCT)": 9,
            "Nurse Aide/Assistant(CNA)": 10,
            "Pharmacy Technician(PTCB)": 11,
            "Clinical Medical Assistant": 13,
            "I want to talk about something else": 14
        }

        course_id = course_id_map.get(lead.get("service"))

        if not course_id:
            log.warning(f"Invalid course for portal: {lead.get('service')}")
            return False

        headers = {
            "Authorization": settings.CLIENT_PORTAL_AUTH
        }

        form_data = {
            "username": settings.CLIENT_PORTAL_USERNAME,
            "password": settings.CLIENT_PORTAL_PASSWORD,
            "location_id": "1",
            "name": lead.get("name"),
            "contact": lead.get("phone"),
            "email": lead.get("email"),
            "class": course_id,
            "source": "Chatbot",
            "date": today_date,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    settings.CLIENT_PORTAL_URL,
                    data=form_data,
                    headers=headers,
                )
                response.raise_for_status()

            log.info("✅ Lead sent to Client Portal successfully")
            return True

        except Exception:
            log.exception("❌ Failed sending lead to Client Portal")
            return False
