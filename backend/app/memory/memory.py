# backend/app/memory/memory.py
from datetime import datetime

# -------------------------------------------------------
# SINGLETON MEMORY STORE
# Ensures ONE shared memory across entire app
# -------------------------------------------------------
class MemoryStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryStore, cls).__new__(cls)
            cls._instance.sessions = {}
        return cls._instance

    # -------------------------------------------------------
    # Ensure session exists
    # -------------------------------------------------------
    def ensure(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "appointment": {
                    "first_name": None,
                    "last_name": None,
                    "email": None,
                    "phone": None,
                    "program": None
                },
                "appointment_stage": None,
                "update_stage": None,
                "lock": None,
                "transcript": []
            }
        return self.sessions[session_id]

    # -------------------------------------------------------
    # Getters
    # -------------------------------------------------------
    def get(self, session_id: str):
        return self.ensure(session_id)

    def get_stage(self, session_id: str):
        return self.ensure(session_id)["appointment_stage"]

    def get_update_stage(self, session_id: str):
        return self.ensure(session_id)["update_stage"]

    def get_lock(self, session_id: str):
        return self.ensure(session_id)["lock"]

    # -------------------------------------------------------
    # Setters
    # -------------------------------------------------------
    def set_stage(self, session_id: str, stage: str):
        self.ensure(session_id)["appointment_stage"] = stage

    def set_update_stage(self, session_id: str, stage: str):
        self.ensure(session_id)["update_stage"] = stage

    def lock(self, session_id: str, mode: str):
        self.ensure(session_id)["lock"] = mode

    def unlock(self, session_id: str):
        mem = self.ensure(session_id)
        mem["lock"] = None
        mem["update_stage"] = None

    # -------------------------------------------------------
    # Appointment fields
    # -------------------------------------------------------
    def set_name(self, session_id: str, full_name: str):
        parts = full_name.strip().split()
        mem = self.ensure(session_id)
        mem["appointment"]["first_name"] = parts[0]
        mem["appointment"]["last_name"] = parts[-1] if len(parts) > 1 else ""

    def set_email(self, session_id: str, email: str):
        self.ensure(session_id)["appointment"]["email"] = email

    def set_phone(self, session_id: str, phone: str):
        self.ensure(session_id)["appointment"]["phone"] = phone

    def set_program(self, session_id: str, program: str):
        self.ensure(session_id)["appointment"]["program"] = program

    # -------------------------------------------------------
    # Lead payload for Make.com
    # -------------------------------------------------------
    def get_lead(self, session_id: str):
        mem = self.ensure(session_id)["appointment"]
        return {
            "name": f"{mem.get('first_name','')} {mem.get('last_name','')}".strip(),
            "email": mem.get("email"),
            "phone": mem.get("phone"),
            "service": mem.get("program")
        }

    # -------------------------------------------------------
    # Summary builder (UI + Transcript safe)
    # -------------------------------------------------------
    def build_summary(self, session_id: str):
        mem = self.ensure(session_id)["appointment"]

        return (
            "Contact Summary\n"
            f"Name: {mem.get('first_name') or ''} {mem.get('last_name') or ''}\n"
            f"Email: {mem.get('email') or ''}\n"
            f"Phone: {mem.get('phone') or ''}\n"
            f"Program: {mem.get('program') or ''}"
        )

    # -------------------------------------------------------
    # Transcript storage
    # -------------------------------------------------------
    def add_message(self, session_id: str, role: str, msg: str):
        self.ensure(session_id)["transcript"].append({
            "role": role,
            "msg": msg,
            "time": datetime.now().isoformat()
        })

    # -------------------------------------------------------
    # SAFE transcript reset (OPTION A support)
    # -------------------------------------------------------
    def reset_transcript(self, session_id: str):
        """
        Clears transcript only.
        Appointment, stages, and locks are untouched.
        Safe for future use if needed.
        """
        mem = self.ensure(session_id)
        mem["transcript"] = []

    # -------------------------------------------------------
    # CLEAR appointment (important)
    # -------------------------------------------------------
    def clear_appointment(self, session_id: str):
        mem = self.ensure(session_id)
        mem["appointment"] = {
            "first_name": None,
            "last_name": None,
            "email": None,
            "phone": None,
            "program": None
        }
        mem["appointment_stage"] = None
        mem["update_stage"] = None
        mem["lock"] = None

    # -------------------------------------------------------
    # Hard reset (manual / admin only)
    # -------------------------------------------------------
    def reset_all(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
