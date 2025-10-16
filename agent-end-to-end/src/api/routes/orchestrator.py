from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from src.utils.logger import get_logger
from src.agents.factory import create_agent
from src.orchestrator.orchestrator import AgentOrchestrator

router = APIRouter()
logger = get_logger(__name__)
orchestrator = AgentOrchestrator()

class ChainRequest(BaseModel):
    chain_config: List[Dict[str, Any]]
    initial_input: Dict[str, Any]

class AgentConfig(BaseModel):
    agent_type: str
    model: str
    version: str | None = "v1"

class ChainRequest(BaseModel):
    agents: List[AgentConfig]
    input_data: Dict[str, Any]

@router.post("/agent/chain/run", tags=["Chain"])
async def run_agent_chain(request: ChainRequest):
    logger.info("🔗 Starting agent chain execution")
    try:
        current_output = request.input_data
        for agent_conf in request.agents:
            logger.info(f"➡️ Running agent: {agent_conf.agent_type}")
            agent = create_agent(
                agent_type=agent_conf.agent_type,
                model=agent_conf.model,
                version=agent_conf.version
            )
            current_output = await agent.run(current_output)
        logger.info("✅ Chain execution completed successfully")
        return {"success": True, "data": current_output}
    except Exception as e:
        logger.error(f"❌ Chain execution failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))