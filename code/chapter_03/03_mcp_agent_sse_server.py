import asyncio
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerSse


async def main():
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as research_server:
        agent = Agent(
            name="Assistant",
            instructions="Use the research tools to perform research.",
            mcp_servers=[research_server],
        )

        print("Running: Get the available research sources")
        result = await Runner.run(agent, "Get the available research sources")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
