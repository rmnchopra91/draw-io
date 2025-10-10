from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Each agent must define how it processes input and returns output.
    """

    def __init__(self, name: str, model: str, prompt: str):
        self.name = name
        self.model = model
        self.prompt = prompt

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent logic on given input and return structured output."""
        pass
