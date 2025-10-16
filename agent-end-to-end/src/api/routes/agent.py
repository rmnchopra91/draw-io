from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.agents.factory import create_agent
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__) 

# Define input schema using Pydantic
class AgentRequest(BaseModel):
    agent_type: str
    model: str
    prompt: Optional[str] = None 
    version: str | None = "v1"
    input_data: Dict[str, Any]

@router.post("/agent/run", tags=["Agent"])
async def run_agent(request: AgentRequest):
    """
    Dynamically create an agent and run it with the provided input.
    """
    logger.info(f"Running agent: {request.agent_type}, model: {request.model}")
    try:
        agent = create_agent(
            agent_type=request.agent_type,
            model=request.model,
            prompt=request.prompt,
            version=request.version
        )
        response = await agent.run(request.input_data)
        logger.info(f"Agent completed successfully: {request.agent_type}")
        return {"success": True, "data": response}
    except Exception as e:
        logger.error(f"❌ Agent failed: {str(e)}") 
        raise HTTPException(status_code=400, detail=str(e))
