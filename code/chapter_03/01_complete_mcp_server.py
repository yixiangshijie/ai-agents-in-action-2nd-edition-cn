# server.py
from mcp.server.fastmcp import FastMCP

# Initialize an MCP server with a name
mcp = FastMCP("DemoServer")


def log(output: str, file_name: str = "server_output.log"):
    """Log output to a file"""
    with open(file_name, "a") as log_file:
        log_file.write(output + "\n")


# Define a resource: greeting://{name}
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting for the given name"""
    print(f"Received request for greeting: {name}")
    log(f"Received request for greeting: {name}")
    return f"Greetings, {name}! (from resource)"


# Define a tool: add(a, b)
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the sum"""
    log(f"Adding {a} and {b}")
    return a + b


# Define a prompt template: welcome(name)
@mcp.prompt()
def welcome(name: str) -> str:
    """Generate a welcome message using the greeting resource"""
    # Incorporate the greeting resource into a prompt message
    greeting_text = get_greeting(name)  # e.g., "Greetings, Alice! (from resource)"
    log(f"Creating welcome message for: {name}")
    return f"{greeting_text} How can I assist you today?"
