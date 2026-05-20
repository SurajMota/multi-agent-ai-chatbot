from app.agents.appointment_agent import AppointmentAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.sentiment_agent import SentimentAgent
from app.agents.intent_agent import IntentAgent
from app.agents.translator_agent import TranslatorAgent

from app.services.analytics_agent import AnalyticsAgent
from app.services.unanswered_logger import UnansweredLogger, is_fallback_response

from app.memory.memory import MemoryStore
from app.core.static_content import STATIC_CONTENT
from server.logger import log


# ---------------------------------------------------
# 🎯 STATIC KEYWORD MAPPING (Deterministic Routing)
# ---------------------------------------------------
STATIC_INTENT_KEYWORDS = {
    "programs": ["programs offered", "list of programs", "what programs do you offer", "available programs"],
    "financial_aid": ["financial aid", "fafsa"],
    "about_us": ["about us", "about"],
    "hours": ["hours", "hours of operation", "campus hours", "opening hours", "working hours", "timings"],
    "address": ["address", "location", "campus address", "where are you located", "where is the campus"],
}

CANCEL_KEYWORDS = {
    "stop", "cancel", "end", "exit",
    "no thanks", "not now", "later",
    "don't want", "dont want"
}


class ChatService:

    def __init__(self):
        self.memory = MemoryStore()
        self.sentiment = SentimentAgent()
        self.intent = IntentAgent()
        self.appointment = AppointmentAgent(self.memory)
        self.knowledge = KnowledgeAgent()
        self.translator = TranslatorAgent()
        self.analytics = AnalyticsAgent()
        self.unanswered = UnansweredLogger()

    async def handle(self, session_id: str, message: str):

        log.info(f"[USER MESSAGE] {message}")

        user_lang = self.translator.detect_language(message)
        processed_message = await self.translator.to_english(message, user_lang)
        msg = processed_message.lower().strip()

        # ---------------------------------------------------
        # 🎯 DIRECT BUTTON → START APPOINTMENT
        # ---------------------------------------------------
        if msg == "book an appointment":
            log.info("[APPOINTMENT] Direct button trigger")

            self.memory.clear_appointment(session_id)
            self.memory.set_stage(session_id, "name")
            self.memory.lock(session_id, "appointment")

            reply = await self.translator.from_english(
                "🧑 Please provide your full name (First and Last)?",
                user_lang
            )
            return {"reply": reply}

        # ---------------------------------------------------
        # 🔁 APPOINTMENT LOOP CHECK
        # ---------------------------------------------------
        lock = self.memory.get_lock(session_id)
        stage = self.memory.get_stage(session_id)
        appointment_stages = {"name", "email", "phone", "program", "summary"}

        if lock == "appointment" or stage in appointment_stages:
            result = await self.appointment.run(session_id, processed_message)

            if isinstance(result, tuple):
                text, meta = result
                reply = await self.translator.from_english(text, user_lang)
                return {"reply": reply, "meta": meta}

            reply = await self.translator.from_english(result, user_lang)
            return {"reply": reply}

        # ---------------------------------------------------
        # 🎯 YES / NO CONFIRMATION
        # ---------------------------------------------------
        if lock != "appointment":

            if msg == "yes":
                log.info("[APPOINTMENT] User confirmed appointment")

                self.memory.clear_appointment(session_id)
                self.memory.set_stage(session_id, "name")
                self.memory.lock(session_id, "appointment")

                reply = await self.translator.from_english(
                    "🧑 Please provide your full name (First and Last)?",
                    user_lang
                )
                return {"reply": reply}

            if msg == "no":
                log.info("[APPOINTMENT] User declined appointment")

                self.memory.clear_appointment(session_id)
                self.memory.unlock(session_id)
                self.memory.set_stage(session_id, None)

                reply = await self.translator.from_english(
                    "No issues, we respect your privacy 😊\n"
                    "How else can I assist you today?",
                    user_lang
                )
                return {"reply": reply}

        # ---------------------------------------------------
        # 🎯 TYPED APPOINTMENT KEYWORDS
        # ---------------------------------------------------
        appointment_keywords = [
            "appointment",
            "book",
            "schedule",
            "enroll",
            "consultation",
            "consultant"
        ]

        if any(k in msg for k in appointment_keywords):
            log.info("[APPOINTMENT] Keyword detected → Showing confirmation")

            reply_text = (
                "To schedule your appointment 📅, I'll need to take your details. 📝\n\n"
                "Please choose from the following:"
            )

            reply = await self.translator.from_english(reply_text, user_lang)

            return {
                "reply": reply,
                "meta": {
                    "type": "confirm_buttons",
                    "buttons": [
                        {"label": "✅ Yes, Setup an Appointment", "value": "yes"},
                        {"label": "❌ No, I don't want to provide", "value": "no"}
                    ]
                }
            }

        # ===================================================
        # 🚀 STATIC CONTENT CHECK (RUN BEFORE INTENT)
        # ===================================================
        for key, keywords in STATIC_INTENT_KEYWORDS.items():
            if any(keyword in msg for keyword in keywords):
                log.info(f"[STATIC] Matched static content: {key}")

                reply = await self.translator.from_english(
                    STATIC_CONTENT[key],
                    user_lang
                )
                return {"reply": reply}

        # ---------------------------------------------------
        # NORMAL INTENT FLOW
        # ---------------------------------------------------
        intent = await self.intent.run(
            session_id=session_id,
            message=processed_message,
            memory=self.memory
        )

        log.info(f"[INTENT] {intent}")

        # ---------------------------------------------------
        # DIRECT APPOINTMENT INTENT
        # ---------------------------------------------------
        if intent == "appointment":
            log.info("[APPOINTMENT] Starting appointment flow from intent")

            self.memory.clear_appointment(session_id)
            self.memory.set_stage(session_id, "name")
            self.memory.lock(session_id, "appointment")

            reply = await self.translator.from_english(
                "🧑 Please provide your full name (First and Last)?",
                user_lang
            )
            return {"reply": reply}

        # ---------------------------------------------------
        # HUMAN AGENT
        # ---------------------------------------------------
        if intent == "human_agent":
            reply = await self.translator.from_english(
                "You can contact us at (718) 460-1717. We will guide you.",
                user_lang
            )
            return {"reply": reply}

        # ---------------------------------------------------
        # KNOWLEDGE (LLM)
        # ---------------------------------------------------
        if intent == "knowledge":

            kb_reply = await self.knowledge.answer(processed_message, session_id)

            if is_fallback_response(kb_reply):
                await self.unanswered.log(
                    session_id=session_id,
                    question=processed_message,
                    intent=intent,
                    language=user_lang,
                    source="knowledge_fallback",
                )

            reply = await self.translator.from_english(kb_reply, user_lang)
            return {"reply": reply}

        # ---------------------------------------------------
        # GENERAL FALLBACK
        # ---------------------------------------------------
        reply = await self.translator.from_english(
            "I'm here to help 😊 What would you like to know?",
            user_lang
        )
        return {"reply": reply}