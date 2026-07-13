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

_last_context = ""  # shared so the Grounding agent can verify answers


@function_tool
def search_knowledge(query: str) -> dict:
    """Retrieve facts relevant to the user’s query."""
    global _last_context
    matches = [doc for doc in _knowledge_db if query.lower() in doc.lower()]
    _last_context = "\n".join(matches)
    print(f"Found {len(matches)} matches for '{query}'")
    return {"status": "ok", "context": _last_context}


@function_tool
def review_answer(answer: str) -> dict:
    """Check that the answer is grounded in the retrieved context."""
    grounded = all(
        snippet.lower() in answer.lower()
        for snippet in _last_context.split("\n")
        if snippet
    )
    verdict = "grounded" if grounded else "possibly ungrounded"
    print(f"Answer review: {verdict}")
    return {"status": verdict, "context_used": _last_context}


rag_agent = Agent(
    name="RAG Agent",
    instructions="""
You are a retrieval‑augmented answering agent.
Always call 'search_knowledge' first to fetch context,
then answer the user using that context verbatim where useful.
""",
    tools=[search_knowledge],
)

grounding_agent = Agent(
    name="Grounding Agent",
    instructions="""
You are a grounding agent that verifies answers.
After the RAG Agent responds, call 'review_answer'
and decide if the reply is fully supported by the provided context.
""",
    tools=[review_answer],
)

question = "Where is the great wall?"

# Run the agent (using await in an async context, or Runner.run_sync in a script)
result = asyncio.run(Runner.run(rag_agent, input=question))
print("RAG Agent Response:")
print(result.final_output)
result = asyncio.run(Runner.run(grounding_agent, input=result.final_output))
print("Grounding Agent Review:")
print(result.final_output)
