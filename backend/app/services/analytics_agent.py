# backend/app/services/analytics_agent.py

from datetime import datetime
from server.logger import log
from app.services.analytics_event_sender import send_event


class AnalyticsAgent:
    """
    Event-based Analytics Agent (Make.com compatible)

    ✔ Sends analytics to Make.com webhook
    ✔ One session_start per session
    ✔ Safe on refresh / reload
    ✔ Does NOT touch Google Sheets directly
    ✔ Does NOT affect chat flow
    """

    def __init__(self):
        # Track sessions already counted as "started"
        self.started_sessions = set()

    # ---------------------------------------------------
    # INTERNAL SENDER
    # ---------------------------------------------------
    async def _send(self, payload: dict):
        try:
            await send_event(payload)
            log.info(f"📊 Analytics sent → {payload['event']}")
        except Exception:
            log.exception("❌ Analytics webhook failed")

    # ---------------------------------------------------
    # CORE EVENT LOGGER
    # ---------------------------------------------------
    async def log_event(
        self,
        session_id: str,
        event: str,
        intent: str | None = None,
        language: str = "en",
        value: int = 1,
        **extra,
    ):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "event": event,
            "intent": intent or "",
            "language": language,
            "value": value,
            **extra,
        }

        await self._send(payload)

    # ---------------------------------------------------
    # SESSION START (ONCE PER SESSION)
    # ---------------------------------------------------
    async def log_session_start(self, session_id: str, language: str = "en"):
        if session_id in self.started_sessions:
            return

        self.started_sessions.add(session_id)

        await self.log_event(
            session_id=session_id,
            event="session_start",
            language=language,
        )

    # ---------------------------------------------------
    # MESSAGE EVENTS
    # ---------------------------------------------------
    async def log_message(
        self,
        session_id: str,
        role: str,
        message: str,
        language: str = "en",
        **kwargs,
    ):
        # User message
        if role == "user":
            await self.log_event(
                session_id=session_id,
                event="message_sent",
                language=language,
            )

    # ---------------------------------------------------
    # INTENT EVENTS
    # ---------------------------------------------------
    async def log_intent(self, session_id: str, intent: str, language: str = "en", **kwargs):
        await self.log_event(
            session_id=session_id,
            event="intent_detected",
            intent=intent,
            language=language,
        )

    # ---------------------------------------------------
    # STATIC BUTTON CLICKS
    # ---------------------------------------------------
    async def log_static_hit(self, session_id: str, intent: str | None = None, language: str = "en", **kwargs):
        await self.log_event(
            session_id=session_id,
            event="static_click",
            intent=intent,
            language=language,
        )

    # ---------------------------------------------------
    # KNOWLEDGE BASE HIT
    # ---------------------------------------------------
    async def log_kb_hit(self, session_id: str, intent: str | None = None, language: str = "en", **kwargs):
        await self.log_event(
            session_id=session_id,
            event="kb_hit",
            intent=intent,
            language=language,
        )

    # ---------------------------------------------------
    # FALLBACK EVENT
    # ---------------------------------------------------
    async def log_fallback(self, session_id: str, intent: str | None = None, language: str = "en"):
        await self.log_event(
            session_id=session_id,
            event="fallback",
            intent=intent,
            language=language,
        )

    # ---------------------------------------------------
    # LEAD SUBMISSION EVENT (OPTIONAL, FUTURE SAFE)
    # ---------------------------------------------------
    async def log_lead_submit(self, session_id: str, language: str = "en", **kwargs):
        await self.log_event(
            session_id=session_id,
            event="lead_submit",
            language=language,
            **kwargs,
        )
