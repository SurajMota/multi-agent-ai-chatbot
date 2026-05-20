import aiohttp
from datetime import datetime
from server.logger import log

# 🔗 Make.com Analytics Webhook
MAKE_ANALYTICS_WEBHOOK_URL = "https://hook.us1.make.com/wmk3zby9ukcpamulzxdl98a313yg8qfi"


async def send_event(payload: dict):
    """
    Core async analytics sender (new implementation)

    ✔ Async
    ✔ Fire-and-forget
    ✔ Never breaks chat
    """

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MAKE_ANALYTICS_WEBHOOK_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=2),
            ):
                pass
    except Exception as e:
        log.warning(f"⚠ Analytics webhook failed silently: {e}")


# ---------------------------------------------------
# BACKWARD-COMPATIBILITY WRAPPER (IMPORTANT)
# ---------------------------------------------------
async def send_analytics_event(
    *,
    session_id: str,
    event: str,
    intent: str = "",
    language: str = "en",
    value: int = 1,
):
    """
    Legacy-compatible wrapper.
    Keeps old imports working without refactor.
    """

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "event": event,
        "intent": intent,
        "language": language,
        "value": value,
    }

    await send_event(payload)
