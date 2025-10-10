from src.agents.impls.simple_agent import SimpleAgent

AGENT_REGISTRY = {
    "simple": SimpleAgent,
}

def get_agent_class(agent_type: str):
    return AGENT_REGISTRY.get(agent_type)
