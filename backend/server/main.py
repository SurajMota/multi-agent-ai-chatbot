from fastapi import APIRouter
from pydantic import BaseModel

from server.logger import log
from server.db import get_conn
from server.utils import now_timestamp

from app.services.chat import ChatService
from app.memory.memory import MemoryStore
from app.services.analytics_event_sender import send_analytics_event

router = APIRouter()

# -------------------------------------------------------
# SERVICES (INITIALIZED ONCE)
# -------------------------------------------------------
memory = MemoryStore()
chat_service = ChatService()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):

    log.info(f"[USER MESSAGE] {req.message}")

    session_data = memory.get(req.session_id)
    history = session_data.get("transcript", [])

    # ✅ Detect first user message in session
    is_first_message = len(history) == 0

    result = await chat_service.handle(req.session_id, req.message)

    reply = result.get("reply")
    meta = result.get("meta", {}) or {}

    language = meta.get("language", "en")
    intent = meta.get("intent", "")

    # ---------------------------------------------------
    # 🔹 ANALYTICS EVENTS (SOURCE OF TRUTH)
    # ---------------------------------------------------

    if is_first_message:
        send_analytics_event(
            session_id=req.session_id,
            event="session_start",
            intent="greeting",
            language=language,
        )

    send_analytics_event(
        session_id=req.session_id,
        event="message_sent",
        intent=intent,
        language=language,
    )

    if meta.get("is_fallback") is True:
        send_analytics_event(
            session_id=req.session_id,
            event="fallback",
            intent="fallback",
            language=language,
        )

    # ---------------------------------------------------
    # SAVE CHAT TRANSCRIPT TO DB (UNCHANGED)
    # ---------------------------------------------------
    try:
        conn = get_conn()
        cur = conn.cursor()

        transcript = "\n".join(
            [f"{m['role']}: {m['msg']}" for m in history]
        )

        cur.execute(
            """
            INSERT INTO conversation_logs
            (session_id, message_count, transcript, timestamp)
            VALUES (?,?,?,?)
            """,
            (
                req.session_id,
                len(history),
                transcript,
                now_timestamp(),
            )
        )

        conn.commit()
        conn.close()

    except Exception:
        log.exception("Failed writing conversation logs")

    return {
        "reply": reply,
        "meta": meta,
        "timestamp": now_timestamp()
    }


@router.get("/health")
def health():
    return {"status": "ok"}
