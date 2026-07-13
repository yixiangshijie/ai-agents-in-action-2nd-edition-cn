import asyncio
import os
import sys

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
        # List tools provided by the MCP server
        tools = await server.list_tools()
        print("Tools provided by the MCP server:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            print(f"  - Parameters: {tool.inputSchema}")
            print("-" * 40)

        tool_result = await server.call_tool(
            "list_directory", 
            dict(path=current_dir))
        content = [text.text for text in tool_result.content]
        print(content[0]) 

if __name__ == "__main__":
    asyncio.run(main())
