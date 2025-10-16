import os
from src.utils.prompt_loader import load_prompt
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.tools.retrieval_tool import RetrievalTool
from src.utils.logger import log_info, log_error
from src.llm.llm_client import LLMClient  # assuming you have a class for LLM calls
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------- Base Agent ----------
class BaseAgent:
    def __init__(self, name: str, model: str, prompt: str):
        self.name = name
        self.model = model
        self.prompt = prompt

    async def run(self, input_data):
        raise NotImplementedError("Subclasses must implement this method")
    
    async def log_call(self, input_data, output_data):
        log_info(f"Agent: {self.name}, Input: {input_data}, Output: {output_data}")

# ---------- Simple Agent ----------
class SimpleAgent(BaseAgent):
    async def run(self, input_data):
        user_text = input_data.get("text", "")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            return {
                "error": "Missing OPENAI_API_KEY. Please set it in your environment."
            }

        # Initialize the LLM using LangChain
        llm = ChatOpenAI(
            model=self.model,
            temperature=0.7,
            openai_api_key=openai_api_key
        )

        # Combine prompt + user text
        final_prompt = f"{self.prompt}\nUser: {user_text}"
        response = await llm.ainvoke([HumanMessage(content=final_prompt)])

        response_dict = {
            "agent": self.name,
            "model": self.model,
            "response": response.content.strip()
        }
        await self.log_call(input_data, response_dict)
        return response_dict

class RetrievalAgent(BaseAgent):
    async def run(self, input_data):
        query = input_data.get("text", "")
        retriever = RetrievalTool()
        contexts = retriever.retrieve(query)

        llm = ChatOpenAI(
            model=self.model,
            temperature=0.5,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        context_text = "\n".join(contexts)
        final_prompt = (
            f"{self.prompt}\n"
            f"Context:\n{context_text}\n\n"
            f"User Question: {query}"
        )

        response = await llm.ainvoke([HumanMessage(content=final_prompt)])

        response_dict =  {
            "agent": self.name,
            "model": self.model,
            "response": response.content.strip(),
            "context_sources": len(contexts)
        }
        
        await self.log_call(input_data, response_dict)
        return response_dict
    

# ---------- Factory ----------
def create_agent(agent_type: str, model: str, prompt: str | None = None, version: str = "v1"):
    logger.info(f"Creating agent → type: {agent_type}, model: {model}, version: {version}")
    prompt_text = load_prompt(agent_type, version)
    if not prompt_text:
        raise ValueError(f"Prompt not found for {agent_type}/{version}")

    return SimpleAgent(name=agent_type, model=model, prompt=prompt_text)
