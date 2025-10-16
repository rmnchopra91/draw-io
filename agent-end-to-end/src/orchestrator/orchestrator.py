from typing import List, Dict, Any
from src.agents.factory import create_agent

class AgentOrchestrator:
    """
    Simple multi-agent orchestrator.
    Runs agents sequentially and passes output of one agent as input to the next.
    """

    async def run_chain(
        self,
        chain_config: List[Dict[str, Any]],
        initial_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        chain_config = [
            {"agent_type": "retrieval", "model": "gpt-4", "version": "v1"},
            {"agent_type": "simple", "model": "gpt-4", "version": "v1"}
        ]
        """
        data = initial_input
        results = []

        for step in chain_config:
            agent = create_agent(
                agent_type=step["agent_type"],
                model=step["model"],
                prompt=None,
                version=step.get("version", "v1")
            )

            result = await agent.run(data)
            results.append({
                "agent_type": step["agent_type"],
                "output": result
            })

            # Pass result to next agent as input
            data = {"text": result.get("response", "")}

        return {
            "chain_results": results,
            "final_output": results[-1]["output"] if results else None
        }
