import asyncio
from src.agents.factory import create_agent

async def main():
    # Create a simple agent using the factory
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>")
    agent = create_agent(
        agent_type="simple",
        model="gpt-4",
        prompt="This is a demo prompt"
    )

    # Run the agent with sample input
    response = await agent.run({"text": "Hello world!"})

    print("Agent Output:", response)

if __name__ == "__main__":
    asyncio.run(main())
