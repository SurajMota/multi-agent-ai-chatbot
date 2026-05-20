# backend/app/routes/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat import ChatService
from app.memory.memory import MemoryStore

router = APIRouter()

chat_service = ChatService()
memory = MemoryStore()


class ChatBody(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat_endpoint(body: ChatBody):

    # ---------------------------------------------------
    # SAVE USER MESSAGE TO TRANSCRIPT
    # ---------------------------------------------------
    memory.add_message(
        session_id=body.session_id,
        role="user",
        msg=body.message
    )

    # ---------------------------------------------------
    # PROCESS MESSAGE
    # ---------------------------------------------------
    result = await chat_service.handle(body.session_id, body.message)

    reply = result.get("reply")
    meta = result.get("meta")

    # ---------------------------------------------------
    # SAVE BOT MESSAGE TO TRANSCRIPT
    # (only if reply is plain text)
    # ---------------------------------------------------
    if reply:
        memory.add_message(
            session_id=body.session_id,
            role="bot",
            msg=reply
        )

    # ---------------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------------
    return {
        "reply": reply,
        "meta": meta
    }

