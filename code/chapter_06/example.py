import asyncio
import os

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

SANDBOX = os.path.dirname(os.path.abspath(__file__))


async def main():
    # Instantiate the servers first…
    servers = [
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

    instructions = """
!-- add your instructions here --
    """

    # …then open them all at once
    async with (
        servers[0] as thinking_srv,
        servers[1] as fs_srv,
    ):
        agent = Agent(
            name="Assistant",
            instructions=instructions,
            mcp_servers=[thinking_srv, fs_srv],
        )
        goal = """
!-- add your goal here --
"""
        print("Running...", goal)
        result = await Runner.run(agent, goal)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
