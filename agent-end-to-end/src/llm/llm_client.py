import openai
import os
import asyncio

class LLMClient:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate(self, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
        )
        return response["choices"][0]["message"]["content"].strip()