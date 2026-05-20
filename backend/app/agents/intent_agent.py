# backend/app/agents/intent_agent.py

from app.agents.base_agent import BaseAgent
from server.logger import log
from app.core.llm import llm_model


class IntentAgent(BaseAgent):
    """
    Classifies user message into one of the following intents:

    - appointment
    - update_appointment
    - lead
    - human_agent
    - knowledge
    - general

    NOTE:
    This agent is used by chat router to decide which agent should reply.
    """

    async def run(self, session_id: str, message: str, memory=None, **kwargs):
        try:
            # Fast rule-based detection (always WIN)
            lowered = message.lower()

            # Human agent request
            if any(k in lowered for k in ["agent", "live agent", "real person", "talk to human", "human", "representative", "support person"]):
                return "human_agent"

            # Appointment booking - This will direct ask name
            if any(k in lowered for k in ["my name is", "i am from", "my number is", "email is"]):
                return "appointment"

            # Appointment update
            if any(k in lowered for k in ["update", "change my appointment", "modify appointment"]):
                return "update_appointment"


            # Now use LLM to classify intent
            prompt = f"""
Classify the user message into one of these intents ONLY:

- appointment
- update_appointment
- lead
- human_agent
- knowledge
- general

Rules:
- If the question is about programs, fees, courses, hours, program schedule → knowledge.
- If user wants human or real agent → human_agent.
- If user provides personal info → appointment.
- If user wants to update it appointment details → update_appointment.
User message: {message}

Return ONLY the intent label.
"""

            model = llm_model()
            raw = await model.acomplete(prompt)
            intent = raw.strip().lower()

            valid_intents = [
                "appointment",
                "update_appointment",
                "lead",
                "human_agent",
                "knowledge",
                "general"
            ]

            return intent if intent in valid_intents else "general"

        except Exception as e:
            log.exception("IntentAgent failed", exc_info=e)
            return "general"
