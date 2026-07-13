import asyncio
import os
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStdio


async def main():
    # Define path to your sample files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Use async context manager to initialize the server
    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", 
                     "@modelcontextprotocol/server-filesystem", 
                     current_dir],
        },
    ) as server:        
        # Create an agent that uses the MCP server
        agent = Agent(
            name="Filesystem Agent",
            instructions="Use the filesystem tools to help the user with their tasks.",
            mcp_servers=[server],
        )

        print("Running: Get the available files")
        result = await Runner.run(agent, "List all file names in the current directory")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
