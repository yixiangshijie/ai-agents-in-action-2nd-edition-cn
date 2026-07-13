import os

from agents.mcp import MCPServerStdio
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Sandbox Filesystem")
SANDBOX = os.path.dirname(os.path.abspath(__file__))

@mcp.tool(name="list_directory",
          description="List all files in the sandbox.")
async def list_directory() -> str:
    """Return the directory contents as a single string."""
    async with MCPServerStdio(
        name="filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", SANDBOX],
        },
    ) as fs:
        res = await fs.call_tool(
            "list_directory", 
            {"path": SANDBOX})
        return res.content[0].text      # assume res.content is a list of Text objects

if __name__ == "__main__":
    mcp.run(transport="sse")            

