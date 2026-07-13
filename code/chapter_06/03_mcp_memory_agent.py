import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServerStdio


async def main():
    # Instantiate the servers first…
    memory_srv = MCPServerStdio(
        name="memory",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory@latest"],
        },
    )

    instructions = """
Follow these steps for each interaction:

1. User Identification:
   - You should assume that you are interacting with default_user
   - If you have not identified default_user, proactively try to do so.

2. Memory Retrieval:
   - Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph
   - Always refer to your knowledge graph as your "memory"
   When using the memory tools, follow these steps:
   a) Input must be valid JSON

3. Memory
   - While conversing with the user, be attentive to any new information that falls into these categories:
     a) Basic Identity (age, gender, location, job title, education level, etc.)
     b) Behaviors (interests, habits, etc.)
     c) Preferences (communication style, preferred language, etc.)
     d) Goals (goals, targets, aspirations, etc.)
     e) Relationships (personal and professional relationships up to 3 degrees of separation)

4. Memory Update:
   - If any new information was gathered during the interaction, update your memory as follows:
     a) Create entities for recurring organizations, people, and significant events
     b) Connect them to the current entities using relations
     b) Store facts about them as observations
    """
    # …then open them all at once
    async with memory_srv:
        agent = Agent(
            name="Memory Agent",
            instructions=instructions,
            mcp_servers=[memory_srv],
        )

        # Input loop for asking questions
        while True:
            try:
                user_input = input("Memory assistant: (or type 'exit' to quit): ")
                if user_input.strip().lower() in ("exit", "quit"):
                    break
                response = await Runner.run(agent, user_input)
                print(response.final_output)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break


if __name__ == "__main__":
    asyncio.run(main())
