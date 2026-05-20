
# backend/app/core/nlu.py

# ---------------------------------------------------
# YES DETECTOR
# ---------------------------------------------------
def is_yes(message: str) -> bool:
    if not message:
        return False

    msg = message.lower().strip()

    return msg in [
        "yes", "y", "yeah", "yep", "sure", "correct",
        "confirm", "yes it is correct", "ok", "okay",
        "affirmative"
    ]


# ---------------------------------------------------
# NO DETECTOR
# ---------------------------------------------------
def is_no(message: str) -> bool:
    if not message:
        return False

    msg = message.lower().strip()

    return msg in [
        "no", "n", "nope", "not correct", "incorrect",
        "change", "cancel", "stop"
    ]


# ---------------------------------------------------
# NEW APPOINTMENT / RESET TRIGGER
# ---------------------------------------------------
def is_new_appointment_trigger(message: str) -> bool:
    if not message:
        return False

    msg = message.lower().strip()

    triggers = [
        "new appointment", "fresh appointment", "start again",
        "restart appointment", "book again", "i want to book again",
        "reset appointment", "enroll", "agent", "start new appointment",
    ]

    return any(t in msg for t in triggers)


# ---------------------------------------------------
# APPOINTMENT INTENT (MISSING EARLIER — ADDED NOW)
# ---------------------------------------------------
def is_appointment_intent(message: str) -> bool:
    msg = message.lower().strip()

    keywords = [
        "appointment",
        "book",
        "schedule",
        "admission",
        "enroll",
        "register",
        "consultation",
        "apply"
    ]

    return any(k in msg for k in keywords)
