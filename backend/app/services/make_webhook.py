# backend/app/services/make_webhook.py

import httpx
from server.logger import log
from app.config import settings
from app.memory.memory import MemoryStore
from app.agents.summary_agent import SummaryAgent

memory = MemoryStore()
summary_agent = SummaryAgent()


def build_transcript_text(messages: list, max_lines: int = 100) -> str:
    """
    Converts transcript list into readable conversation text.

    Example:
    bot: Hello! How can I help you today?
    user: I would like to apply
    """
    # Keep only the last `max_lines` messages
    trimmed_messages = messages[-max_lines:]

    lines = []
    for m in trimmed_messages:
        role = m.get("role", "unknown")
        msg = m.get("msg", "")
        lines.append(f"{role}: {msg}")
    return "\n".join(lines)


def build_fallback_summary(lead: dict, messages: list) -> str:
    """
    Safe fallback summary if AI summary fails.
    This guarantees Make.com ALWAYS receives a summary.
    """
    intent = "scheduled an appointment"

    return (
        f"User {intent}.\n"
        f"Name: {lead.get('name')}\n"
        f"Email: {lead.get('email')}\n"
        f"Phone: {lead.get('phone')}\n"
        f"Program: {lead.get('service')}\n"
        f"Total messages: {len(messages)}"
    )


async def send_to_make(session_id: str, lead: dict):
    """
    Sends final appointment data to Make.com including:
    - Lead details
    - AI summary (with fallback)
    - Full chat transcript
    """

    if not settings.MAKE_WEBHOOK_URL:
        log.warning("MAKE_WEBHOOK_URL missing — skipping Make.com")
        return False

    # ---------------------------------------------------
    # FETCH TRANSCRIPT
    # ---------------------------------------------------
    session = memory.get(session_id)
    messages = session.get("transcript", [])

    transcript_text = build_transcript_text(messages)

    # ---------------------------------------------------
    # BUILD SUMMARY (AI → fallback)
    # ---------------------------------------------------
    summary_text = None

    try:
        # ⚠️ This may fail if SummaryAgent signature mismatches
        summary_text = await summary_agent.run(messages)
    except Exception as e:
        log.warning(f"AI summary failed, using fallback: {e}")

    if not summary_text or not isinstance(summary_text, str):
        summary_text = build_fallback_summary(lead, messages)

    # ---------------------------------------------------
    # FINAL PAYLOAD
    # ---------------------------------------------------
    payload = {
        "name": lead.get("name"),
        "email": lead.get("email"),
        "phone": lead.get("phone"),
        "program": lead.get("service"),
        "summary": summary_text,
        "transcript": transcript_text
    }

    # ---------------------------------------------------
    # SEND TO MAKE.COM
    # ---------------------------------------------------
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(settings.MAKE_WEBHOOK_URL,
                                         json=payload)
            response.raise_for_status()

        log.info("✅ Lead + summary + transcript sent to Make.com")
        return True

    except Exception as e:
        log.exception("❌ Failed sending data to Make.com")
        return False
