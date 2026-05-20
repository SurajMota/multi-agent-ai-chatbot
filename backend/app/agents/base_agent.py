# backend/app/agents/base_agent.py

class BaseAgent:
    """
    Base class for all agents.
    """

    def __init__(self, memory=None):
        self.memory = memory

    def json(self, payload: dict):
        """
        Allows agents to return JSON instructions to frontend.
        Used for program dropdown triggers.
        """
        return payload

    async def run(self, session_id: str, message: str, memory=None, **kwargs):
        raise NotImplementedError("Each agent must implement run()")
