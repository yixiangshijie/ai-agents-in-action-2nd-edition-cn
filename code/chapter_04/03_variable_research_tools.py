import random

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Research Tools")


@mcp.tool()
def get_research_sources() -> list[str]:
    """Provides 0 to 3 random research sources."""
    search_sources = [
        "Wikipedia",
        "Google",
        "YouTube",
    ]
    num_sources = random.randint(0, 3)
    if num_sources == 0:
        return []
    return random.sample(search_sources, num_sources)
