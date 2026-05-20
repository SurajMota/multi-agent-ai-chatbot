# backend/app/agents/general_agent.py

from app.agents.base_agent import BaseAgent
from app.core.llm import llm_model
from server.logger import log

class GeneralAgent(BaseAgent):
    """
    Handles normal, non-appointment, non-knowledge,
    non-update queries.

    If user message is normal, reply using the LLM.
    """

    async def run(self, session_id: str, message: str, memory=None, **kwargs):
        try:
            prompt = f"""
You are a helpful, friendly AI assistant for a career training school.

Rules:
- Keep answers short, clear, professional.
- Do NOT enter appointment mode.
- Do NOT ask for personal details.
- If user asks about booking → let router trigger appointment flow.
- If the user requests program info → KnowledgeAgent will respond.
- You ONLY answer general conversational or basic FAQs.

User message:
{message}
"""

            model = llm_model()
            reply = await model.acomplete(prompt)

            return reply.strip()

        except Exception as e:
            log.exception("GeneralAgent failed", exc_info=e)
            return "I'm here to help! Could you repeat that?"
