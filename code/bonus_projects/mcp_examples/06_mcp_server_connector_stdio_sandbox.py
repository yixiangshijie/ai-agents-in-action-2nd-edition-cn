import asyncio
import os
from pathlib import Path
import sys

from agents.mcp import MCPServerStdio
from agents.mcp import MCPServerStdio, MCPServerStdioParams

SCRIPT = Path(__file__).with_name(
    "06_mcp_wrapped_hosted_server.py").resolve()

async def main():
    async with MCPServerStdio(
        name="Sandbox Filesystem",
        params=MCPServerStdioParams(
            command="mcp",
            args=["run", str(SCRIPT)],
        ),
    ) as server:        
        # List tools provided by the MCP server
        tools = await server.list_tools()
        print("Tools provided by the MCP server:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            print(f"  - Parameters: {tool.inputSchema}")
            print("-" * 40)

        tool_result = await server.call_tool(
            "list_directory", 
            None)
        content = [text.text for text in tool_result.content]
        print(content[0]) 

if __name__ == "__main__":
    asyncio.run(main())
