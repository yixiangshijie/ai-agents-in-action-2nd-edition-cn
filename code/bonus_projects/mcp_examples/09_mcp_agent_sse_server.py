import asyncio
import os
from pathlib import Path
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStdio


async def main():
    # Define path to your sample files
    SCRIPT = Path(__file__).with_name("01_claude_mcp_server.py").resolve()

    # Use async context manager to initialize the server
    async with MCPServerStdio(
        name="Filesystem Server, via mcp",
        params={
            "command": "mcp",
            "args": ["run", 
                     str(SCRIPT), 
                     ],
        }
    ) as server:
        # List tools provided by the MCP server
        tools = await server.list_tools()
        print("Tools provided by the MCP server:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # Create an agent that uses the MCP server
        agent = Agent(
            name="Filesystem Agent",
            instructions="Use the tools to help the user with their tasks.",
            mcp_servers=[server],
        )

        print("Running: Get the available research sources")
        result = await Runner.run(agent, "List the research sources")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
