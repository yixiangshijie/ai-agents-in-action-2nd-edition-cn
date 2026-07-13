import asyncio
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStdio


async def create_search_server() -> MCPServerStdio:
    server = MCPServerStdio(
        name="Brave Search",
        params={
            "command": "npx",
            "args": ["-y", "@anthropic/brave-search-mcp"],
            "env": {"BRAVE_API_KEY": os.environ["BRAVE_API_KEY"]},
        },
    )
    await server.connect()
    return server
