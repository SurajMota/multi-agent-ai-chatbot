# backend/app/agents/sentiment_agent.py

from app.agents.base_agent import BaseAgent
from app.core.llm import llm_model
from server.logger import log


class SentimentAgent(BaseAgent):
    """
    Detects negative emotions or emergencies.
    - High priority: emergency detection
    - Medium priority: anger/frustration/confusion
    - Normal: return None → other agents handle it
    """

    async def run(self, session_id: str, message: str, memory=None, **kwargs):
        msg = message.lower().strip()

        try:
            # -----------------------------------------
            # 1) EMERGENCY / URGENT KEYWORDS (Instant)
            # -----------------------------------------
            emergency_words = [
                "urgent", "emergency", "immediately", "right now",
                "bleeding", "accident", "danger", "help me",
                "i need help", "i need immediate help", "serious"
            ]

            if any(word in msg for word in emergency_words):
                return (
                    "⚠️ It sounds like this may be an emergency. "
                    "Please contact emergency services or a medical professional immediately. "
                    "I'm here to assist, but urgent issues require human help."
                )

            # -----------------------------------------
            # 2) Use LLM for sentiment detection
            # -----------------------------------------
            prompt = f"""
Classify the user's emotional tone into one of these labels ONLY:

- anger
- frustration
- confusion
- neutral
- positive

User message: "{message}"

Return ONLY the label.
"""

            model = llm_model()
            raw = await model.acomplete(prompt)
            sentiment = raw.lower().strip()

            # -----------------------------------------
            # 3) Emotion-based responses
            # -----------------------------------------
            if sentiment in ["anger", "frustration"]:
                return (
                    "😟 I’m sorry you’re feeling this way. "
                    "Let me help fix this — can you tell me what went wrong?"
                )

            if sentiment == "confusion":
                return (
                    "I understand this may seem confusing. "
                    "Let me clarify it for you — what would you like help with?"
                )

            # -----------------------------------------
            # 4) Neutral or positive → continue normal flow
            # -----------------------------------------
            return None

        except Exception as e:
            log.exception("SentimentAgent failed", exc_info=e)
            return None
