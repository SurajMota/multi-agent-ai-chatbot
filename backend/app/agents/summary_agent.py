# backend/app/agents/summary_agent.py

from app.agents.base_agent import BaseAgent
from app.core.llm import llm_model
from server.logger import log


class SummaryAgent(BaseAgent):
    """
    Creates a clean conversation summary for:
    - Google Sheets logging
    - Make.com appointment webhook
    - CRM systems
    """

    async def run(self, session_id: str, message: str, memory=None, **kwargs):
        try:
            if memory is None:
                return ""

            # Fetch conversation history
            history = memory.get(session_id)

            if not history or len(history) == 0:
                return ""

            # Convert memory list to readable transcript
            conversation_text = ""
            for entry in history:
                role = entry["role"]
                content = entry["content"]
                conversation_text += f"{role.upper()}: {content}\n"

            # Build prompt for clean summary
            prompt = f"""
You are a summarization assistant.

Create a VERY clean and short summary of the following conversation.
DO NOT include filler text, greetings, or small talk.

Focus on:
- User’s intent
- Key details provided (name, email, phone, program, appointment request, etc.)
- Any important follow-up actions required

Conversation transcript:
{conversation_text}

Provide the summary in 3–5 bullet points.
"""

            model = llm_model()
            summary = await model.acomplete(prompt)

            return summary.strip()

        except Exception as e:
            log.exception("SummaryAgent failed", exc_info=e)
            return ""
