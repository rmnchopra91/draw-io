from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, prompt: str):
        self.prompt = prompt

    @abstractmethod
    async def run(self, input_text: str) -> str:
        pass
