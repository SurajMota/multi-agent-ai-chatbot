# backend/app/router.py
import re

def detect_intent(message: str) -> str:
    msg = message.lower().strip()

    # --- APPOINTMENT START PHRASES ---
    appointment_triggers = [
        "book", "appointment", "schedule",
        "make an appointment", "setup an appointment",
        "take my details", "yes_take_details", "agent","Human",
        "yes, take my details", "my name is",  "my number is", "my email is","agent"
    ]

    if any(x in msg for x in appointment_triggers):
        return "appointment"

    # --- UPDATE APPOINTMENT ---
    if any(x in msg for x in ["update", "change", "modify"]):
        return "update_appointment"

    # --- KNOWLEDGE BASE ---
    knowledge_keywords = [
        "program", "course", "fee", "cost",
        "timing", "schedule", "location"
    ]
    if any(k in msg for k in knowledge_keywords):
        return "knowledge"

    if "?" in msg:
        return "knowledge"

    return "general"
