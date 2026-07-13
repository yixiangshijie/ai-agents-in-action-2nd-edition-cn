import asyncio
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio, MCPServerStdioParams

SCRIPT = Path(__file__).with_name(
    "07_mcp_agent_hosted_server.py").resolve()

async def main():
    async with MCPServerStdio(
        name="Research Tools",
        params=MCPServerStdioParams(
            command="mcp",
            args=["run", str(SCRIPT)],
        ),
    ) as research_server:
        agent = Agent(
            name="Assistant",
            instructions="""
Use the research tools to perform and plan research.""",
            mcp_servers=[research_server],
        )

        input = """
Get the research plan for the book 
'The Hitchhiker's Guide to the Galaxy'"""
        print("Running: Get the research plan")
        result = await Runner.run(agent, input)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
