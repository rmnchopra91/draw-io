from src.agents.base import BaseAgent
from typing import Dict, Any

class SimpleAgent(BaseAgent):
    """
    A simple agent example that just formats a response using a prompt.
    Later we’ll integrate LangChain components here.
    """

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_input = input_data.get("text", "")
        return {
            "agent": self.name,
            "model": self.model,
            "response": f"{self.prompt} — User said: {user_input}"
        }
