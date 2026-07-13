import asyncio

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Simple in‑memory knowledge base
_knowledge_db = [
    "The Eiffel Tower is in Paris and was built for the 1889 Exposition.",
    "Mount Everest is the tallest mountain above sea level at 8,848 m.",
    "The Great Wall of China extends more than 21,000 km across northern China.",
    "The Amazon Rainforest generates roughly 20 % of Earth’s oxygen supply.",
    "The Moon orbits Earth at an average distance of 384,400 km.",
]


@function_tool
def search_knowledge(query: str) -> dict:
    """Search the knowledge database for relevant facts."""
    matches = [doc for doc in _knowledge_db if query.lower() in doc.lower()]
    print(f"Found {len(matches)} matches for '{query}'")
    return {"status": "ok", "context": "\n".join(matches)}


agent = Agent(
    name="RAG Agent",
    instructions="""
You are a retrieval‑augmented answering agent.
Always call 'search_knowledge' first 
break your query into smaller parts if needed
to fetch relevant context for the user's query.
Respond using the retrieved context in your answer.
""",
    tools=[search_knowledge],
)

question = "Where is the great wall?"

# Run the agent (using await in an async context, or Runner.run_sync in a script)
result = asyncio.run(Runner.run(agent, input=question))
print(result.final_output)
