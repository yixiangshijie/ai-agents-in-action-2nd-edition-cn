import asyncio
import os
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio, MCPServerStdioParams

SANDBOX = os.path.dirname(os.path.abspath(__file__))
SCRIPT = Path(__file__).with_name("01_research_tools_mcp_server.py").resolve()


async def main():
    # Instantiate the agents first…
    research_agent = Agent(
        name="Research Agent",
        instructions="""
You are a research assistant.
Your role is to find research sources.
""",
    )
    thinking_agent = Agent(
        name="Thinking Agent",
        instructions="""
You are a research assistant.
Your role is to plan the research.
""",
    )
    filesystem_agent = Agent(
        name="Filesystem Agent",
        instructions="""
You are a research assistant.
Your role is to write the research plan as a text file.
""",
    )
    # Instantiate the servers next…
    servers = [
        MCPServerStdio(
            name="Research Tools",
            params=MCPServerStdioParams(
                command="mcp",
                args=["run", str(SCRIPT)],
            ),
        ),
        MCPServerStdio(
            name="sequential-thinking",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            },
        ),
        MCPServerStdio(
            name="filesystem",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", SANDBOX],
            },
        ),
    ]

    # …then open them all at once
    async with (
        servers[0] as research_srv,
        servers[1] as thinking_srv,
        servers[2] as fs_srv,
    ):
        goal = """
Produce a research plan to find the book 'The Hitchhiker's Guide to the Galaxy'
"""
        print("Running...", goal)
        research_agent.mcp_servers = [research_srv]
        result = await Runner.run(research_agent, goal)
        thinking_agent.mcp_servers = [thinking_srv]
        result = await Runner.run(thinking_agent, result.final_output)
        filesystem_agent.mcp_servers = [fs_srv]
        result = await Runner.run(filesystem_agent, result.final_output)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
