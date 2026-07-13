import asyncio
from pathlib import Path

from agents.mcp import MCPServerSse

# Run this example with: 06_mcp_multiple_tools_hosted_server.py

async def main():
    async with MCPServerSse(
        name="Sandbox Filesystem",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        # List tools provided by the MCP server
        tools = await server.list_tools()
        print("Tools provided by the MCP server:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            print(f"  - Parameters: {tool.inputSchema}")
            print("-" * 40)

        tool_result = await server.call_tool("list_directory", None)
        content = [text.text for text in tool_result.content]
        print(content[0])

        tool_result = await server.call_tool(
            "read_file", dict(path="01_claude_mcp_server.py")
        )
        content = [text.text for text in tool_result.content]
        print(content[0])


if __name__ == "__main__":
    asyncio.run(main())
