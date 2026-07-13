from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Time Travel Tracker")

# In-memory journal state (list of entries)
_journal = []


@mcp.tool()
def record_event(entry: str) -> dict:
    """Add a new travel event to the journal."""
    _journal.append(entry)
    print(f"Event recorded: {entry}")
    return {"status": "recorded", "entry": entry}


@mcp.tool()
def load_journal() -> dict:
    """Load the current travel journal entries."""
    print("Loading journal entries...")
    return {"status": "loaded", "journal": "\n".join(_journal)}


if __name__ == "__main__":
    mcp.run(transport="sse")
