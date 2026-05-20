# backend-agents-appointment_agent.py
import re
from app.core.nlu import is_yes, is_no
from app.memory.memory import MemoryStore
from app.services.make_webhook import send_to_make


class AppointmentAgent:
    def __init__(self, memory: MemoryStore):
        self.memory = memory

    # -------------------------------
    # Helpers
    # -------------------------------
    def extract_email(self, text: str):
        match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return match.group(0) if match else None

    def extract_phone(self, text: str):
        match = re.search(r"\b\d{10}\b", text)
        return match.group(0) if match else None

    def extract_name(self, text: str):
        cleaned = re.sub(
            r"\b(my name is|i am|this is)\b",
            "",
            text,
            flags=re.IGNORECASE
        ).strip()
        return cleaned if cleaned.replace(" ", "").isalpha() else None
    
    # -------------------------------
    # Contact Summary
    # -------------------------------
    def build_summary(self, session_id: str):
        lead = self.memory.get_lead(session_id)

        return (
            "📝 <strong style='font-weight:900;'>Contact Summary</strong>\n"
            f"👤 <strong style='font-weight:900;'>Name:</strong> {lead.get('name') or '-'}\n"
            f"📧 <strong style='font-weight:900;'>Email:</strong> {lead.get('email') or '-'}\n"
            f"📞 <strong style='font-weight:900;'>Phone:</strong> {lead.get('phone') or '-'}\n"
            f"🎓 <strong style='font-weight:900;'>Program:</strong> {lead.get('service') or '-'}"
        )

    # -------------------------------
    # MAIN FLOW
    # -------------------------------
    async def run(self, session_id: str, message: str):

        stage = self.memory.get_stage(session_id)
        lock = self.memory.get_lock(session_id)

        # -------------------------------
        # UPDATE MODE
        # -------------------------------
        if lock == "update":
            return await self.handle_update_flow(session_id, message)

        # -------------------------------
        # NAME
        # -------------------------------
        if stage == "name":
            name = self.extract_name(message)
            if not name:
                return "❌ Please enter a valid full name."

            self.memory.set_name(session_id, name)
            self.memory.set_stage(session_id, "email")
            return "📧 Perfect! Now, what's your email?"

        # -------------------------------
        # EMAIL
        # -------------------------------
        if stage == "email":
            email = self.extract_email(message)
            if not email:
                return "❌ Please enter a valid email."

            self.memory.set_email(session_id, email)
            self.memory.set_stage(session_id, "phone")
            return "📞 Got it! Please share your phone number."

        # -------------------------------
        # PHONE
        # -------------------------------
        if stage == "phone":
            phone = self.extract_phone(message)
            if not phone:
                return "❌ Please enter a valid 10-digit phone number."

            self.memory.set_phone(session_id, phone)
            self.memory.set_stage(session_id, "program")

            return (
                "🎓 Choose a program from the list below:",
                {
                    "type": "program_dropdown",
                    "options": [
                        "Nursing",
                        "Medical Assistant (RMA)",
                        "Pharmacy Technician (PTCB)",
                        "EPA Technician 608 Certification"
                    ]
                }
            )

        # -------------------------------
        # PROGRAM
        # -------------------------------
        if stage == "program":
            self.memory.set_program(session_id, message)
            self.memory.set_stage(session_id, "summary")

            return (
                self.build_summary(session_id),
                {
                    "type": "confirm_buttons",
                    "buttons": [
                        {"label": "✅ Yes, it is correct", "value": "yes"},
                        {"label": "✏️ No, I want to update", "value": "no"}
                    ]
                }
            )

        # -------------------------------
        # SUMMARY CONFIRMATION
        # -------------------------------
        if stage == "summary":

            if is_yes(message):
                lead = self.memory.get_lead(session_id)
                await send_to_make(session_id, lead)

                self.memory.clear_appointment(session_id)
                self.memory.unlock(session_id)
                self.memory.set_stage(session_id, None)

                return (
                    "✅ Thank you! Our team will contact you shortly.\n\n"
                    "How else can I help you today? 😊"
                )

            if is_no(message):
                self.memory.lock(session_id, "update")
                self.memory.set_update_stage(session_id, None)

                return (
                    "What would you like to update?",
                    {
                        "type": "confirm_buttons",
                        "buttons": [
                            {"label": "👤 Update Name", "value": "update name"},
                            {"label": "📧 Update Email", "value": "update email"},
                            {"label": "📞 Update Phone", "value": "update phone"},
                            {"label": "🎓 Update Program", "value": "update program"}
                        ]
                    }
                )

            return "Please confirm using the buttons above."

        return "⚠️ Something went wrong. Please try again."

    # -------------------------------
    # UPDATE FLOW
    # -------------------------------
    async def handle_update_flow(self, session_id: str, message: str):

        stage = self.memory.get_update_stage(session_id)
        msg = message.lower().strip()

        # -------------------------------
        # SELECT FIELD
        # -------------------------------
        if stage is None:

            if msg in ["update name", "update email", "update phone", "update program"]:
                self.memory.set_update_stage(session_id, msg.split()[-1])

                if msg == "update program":
                    return (
                        "🎓 Choose the updated program:",
                        {
                            "type": "program_dropdown",
                            "options": [
                                "Diagnostic Medical Sonographer (DMS)",
                                "Nurse Aide/Assistant",
                                "Pharmacy Technician (PTCB)",
                                "Dialysis Technician",
                                "Phlebotomy Technician",
                                "Patient Care Technician (PCT)",
                                "Electrocardiography (EKG)",
                                "EKG & Phlebotomy",
                                "Nursing",
                                "EKG Technician",
                                "Medical Assistant (RMA)",
                                "Clinical Medical Assistant"
                                
                                
                            ]
                        }
                    )

                field_map = {
                    "update name": "👤 Enter your updated name.",
                    "update email": "📧 Enter your updated email.",
                    "update phone": "📞 Enter your updated phone number."
                }

                return field_map[msg]

            return "Please choose one of the update options above."

        # -------------------------------
        # APPLY UPDATE
        # -------------------------------
        if stage == "name":
            name = self.extract_name(message)
            if not name:
                return "❌ Please enter a valid name."
            self.memory.set_name(session_id, name)

        elif stage == "email":
            email = self.extract_email(message)
            if not email:
                return "❌ Please enter a valid email."
            self.memory.set_email(session_id, email)

        elif stage == "phone":
            phone = self.extract_phone(message)
            if not phone:
                return "❌ Please enter a valid phone number."
            self.memory.set_phone(session_id, phone)

        elif stage == "program":
            self.memory.set_program(session_id, message)

        # Back to summary
        self.memory.set_update_stage(session_id, None)
        self.memory.lock(session_id, None)
        self.memory.set_stage(session_id, "summary")

        return (
            self.build_summary(session_id),
            {
                "type": "confirm_buttons",
                "buttons": [
                    {"label": "✅ Yes, it is correct", "value": "yes"},
                    {"label": "✏️ No, I want to update", "value": "no"}
                ]
            }
        )
