from typing import Any, Dict
from src.agents.registry import get_agent_class
from src.agents.base import BaseAgent

def create_agent(agent_type: str, model: str, prompt: str, **kwargs: Dict[str, Any]) -> BaseAgent:
    """
    Factory method to create agent instances dynamically.
    Example: agent = create_agent("simple", model="gpt-4", prompt="Hello Agent")
    """
    agent_class = get_agent_class(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class(name=agent_type, model=model, prompt=prompt)
