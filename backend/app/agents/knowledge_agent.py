# backend/app/agents/knowledge_agent.py

from server.logger import log
from app.agents.rag_agent import RAGAgent
from app.memory.memory import MemoryStore
from app.core.static_content import STATIC_CONTENT
import re

memory = MemoryStore()

# -------------------------------------------------------
# 🧹 CLEAN TEXT FUNCTION
# -------------------------------------------------------

def clean_text(text: str) -> str:
    if not text:
        return text
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = text.replace("�", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    return text


# -------------------------------------------------------
# 🔎 NORMALIZE MESSAGE (SAFE CHECK ONLY)
# -------------------------------------------------------

def normalize_msg_for_checks(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


# -------------------------------------------------------
# 🧠 PROGRAM FEE MAP (UNCHANGED)
# -------------------------------------------------------

PROGRAM_FEES = {
    "medical assistant": ("Medical Assistant (RMA)", "$12400"),
    "medical assistant program": ("Medical Assistant (RMA)", "$12400"),
    "rma": ("Medical Assistant (RMA)", "$12400"),
    "dialysis": ("Dialysis Technician", "$2050"),
    "dialysis technician": ("Dialysis Technician", "$2050"),
    "phlebotomy": ("Phlebotomy Technician", "$930"),
    "phlebotomy technician": ("Phlebotomy Technician", "$930"),
    "patient care technician": ("Patient Care Technician (PCT)", "$1279"),
    "pct": ("Patient Care Technician (PCT)", "$1279"),
    "pharmacy technician": ("Pharmacy Technician (PTCB)", "$1449"),
    "ptcb": ("Pharmacy Technician (PTCB)", "$1449"),
    "electrocardiography": ("Electrocardiography (EKG)", "$630"),
    "ekg": ("Electrocardiography (EKG)", "$630"),
    "ekg technician": ("EKG Technician", "$730"),
    "ekg & phlebotomy": ("EKG & Phlebotomy", "$1279"),
    "nurse aide": ("Nurse Aide/Assistant (CNA)", "$1439"),
    "cna": ("Nurse Aide/Assistant (CNA)", "$1439"),
    "diagnostic medical sonography": ("Diagnostic Medical Sonography (DMS)", "$40000"),
    "dms": ("Diagnostic Medical Sonography (DMS)", "$40000"),
    "clinical medical assistant": ("Clinical Medical Assistant", "$4999"),
}

ALL_FEES_RESPONSE = """
The fees for our programs are as follows:

• Medical Assistant (RMA): $12400
• Dialysis Technician: $2050
• Phlebotomy Technician: $930
• Patient Care Technician (PCT): $1279
• Pharmacy Technician (PTCB): $1449
• Electrocardiography (EKG): $630
• EKG & Phlebotomy: $1279
• Nurse Aide/Assistant (CNA): $1439
• EKG Technician: $730
• Diagnostic Medical Sonography (DMS): $40000
• Clinical Medical Assistant: $4999

Fees include tuition, books/equipment, and registration as applicable.
"""

# -------------------------------------------------------
# CONVERSATIONAL RESPONSES (UNCHANGED)
# -------------------------------------------------------

GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

SMALL_TALK_RESPONSES = {
    "how are you": "I'm doing great, thank you for asking! 😊 How can I assist you today?",
    "who are you": "I'm the AI Student Assistant for NY Medical Training. 😊 How may I help you today?",
    "tell me who are you": "I'm the AI Student Assistant for NY Medical Training. 😊 How may I help you today?",
    "what can you do": "I can help you with program details, fees, admissions, financial aid, class schedules, and more. 😊",
    "thank you": "You're very welcome! 😊 Let me know if you need anything else.",
    "thanks": "You're very welcome! 😊 Let me know if you need anything else."
}

CHAT_END_KEYWORDS = {"bye", "goodbye", "see you", "exit", "quit", "good bye"}
PRICE_KEYWORDS = {"fee", "fees", "price", "cost", "tuition", "charges"}


# -------------------------------------------------------
# KNOWLEDGE AGENT
# -------------------------------------------------------

class KnowledgeAgent:
    def __init__(self):
        self.rag = RAGAgent()

    async def answer(self, message: str, session_id: str = "kb"):

        msg = message.lower().strip()
        msg_check = normalize_msg_for_checks(message)
        mem = memory.get(session_id)

        log.info("[KNOWLEDGE] Processing message")

        campuses = {"flushing", "manhattan", "garden city"}

        # ------------------------------------------------
        # 🔁 HOURS FOLLOW-UP (UNCHANGED)
        # ------------------------------------------------
        if mem.get("pending_hours") and msg in campuses:
            original_query = mem.get("last_hours_query", "hours of operation")
            mem["pending_hours"] = False
            combined_query = f"{original_query} {msg}"

            rag_answer = await self.rag.run(
                session_id=session_id,
                message=combined_query
            )

            if rag_answer:
                return clean_text(rag_answer)

        # ------------------------------------------------
        # ✅ HARD-CODE: HOURS (DETERMINISTIC)
        # ------------------------------------------------
        hours_triggers = [
            "hours",
            "hours of operation",
            "campus hours",
            "opening hours",
            "working hours",
            "timings"
        ]

        if any(t in msg_check for t in hours_triggers):
            if "hours" in STATIC_CONTENT:
                return clean_text(STATIC_CONTENT["hours"])

        # ------------------------------------------------
        # ✅ HARD-CODE: ADDRESS / LOCATION 
        # ------------------------------------------------
        address_triggers = [
            "address",
            "location",
            "where are you located",
            "where is the campus",
            "campus address",
            "campus"
        ]

        if any(t in msg_check for t in address_triggers):
            if "address" in STATIC_CONTENT:
                return clean_text(STATIC_CONTENT["address"])

        # ------------------------------------------------
        # GREETINGS
        # ------------------------------------------------
        if msg in GREETINGS:
            return "Hello! 😊 How can I assist you today?"

        # ------------------------------------------------
        # SMALL TALK
        # ------------------------------------------------
        if msg in SMALL_TALK_RESPONSES:
            return SMALL_TALK_RESPONSES[msg]

        # ------------------------------------------------
        # CHAT END
        # ------------------------------------------------
        if msg in CHAT_END_KEYWORDS:
            return (
                "Thank you for chatting with us today! 😊 "
                "If you have any more questions, feel free to come back anytime."
            )

        # ------------------------------------------------
        # 🎯 FEE LOGIC (UNCHANGED)
        # ------------------------------------------------
        if any(k in msg for k in PRICE_KEYWORDS):
            for keyword, (display_name, fee) in PROGRAM_FEES.items():
                if keyword in msg:
                    log.info(f"[FEE] Specific program fee detected: {keyword}")
                    return f"The total fee for {display_name} is {fee}."
            return ALL_FEES_RESPONSE

        # ------------------------------------------------
        # STATIC CONTENT
        # ------------------------------------------------
        static_key = detect_static_intent(msg)
        if static_key:
            return STATIC_CONTENT[static_key]

        # ------------------------------------------------
        # RAG FALLBACK (UNCHANGED)
        # ------------------------------------------------
        rag_answer = await self.rag.run(
            session_id=session_id,
            message=message
        )

        if rag_answer:
            rag_answer = clean_text(rag_answer)

            if "which campus" in rag_answer.lower():
                mem["pending_hours"] = True
                mem["last_hours_query"] = msg

                return (
                    rag_answer
                    + "\n\nAvailable campuses:\n"
                    "• Flushing\n"
                    "• Manhattan\n"
                    "• Garden City"
                )

            return rag_answer

        # ------------------------------------------------
        # FINAL FALLBACK
        # ------------------------------------------------
        mem["pending_knowledge"] = msg
        return (
            "I understand this may seem confusing. "
            "Could you please tell me what information you’re looking for?"
        )


def detect_static_intent(msg: str):
    msg = msg.lower().strip()

    if msg in ["about", "about us", "about you"]:
        return "about_us"
    if msg in ["programs", "courses", "course list"]:
        return "programs"
    if msg in ["financial aid", "financial", "aid"]:
        return "financial_aid"

    return None