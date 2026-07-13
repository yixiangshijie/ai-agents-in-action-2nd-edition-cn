import asyncio

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Simple in‑memory knowledge base
_special_knowledge_db = [
    "Nebula Forge engine spins antimatter rings for gravity control.",
    "Solaris Glacier absorbs heat, releasing luminescent icefire at dusk.",
    "Quantum Bark trees emit entangled photons guiding nocturnal insect migrations.",
    "Aether Silk fabric self-weaves repairs within fourteen-millisecond microtears.",
    "Chrono Coral reefs rewind water currents three minutes every solstice.",
]

# benchmarks for special knowledge
_benchmarks = [
    {"q": "Nebula Forge engine spins what?", "a": "antimatter", "wrong": "fusion"},
    {
        "q": "Solaris Glacier releases luminescent what?",
        "a": "icefire",
        "wrong": "lava",
    },
    {"q": "Quantum Bark trees emit what?", "a": "photons", "wrong": "spores"},
    {"q": "Aether Silk fabric repairs what?", "a": "microtears", "wrong": "threads"},
    {"q": "Chrono Coral reefs rewind what?", "a": "currents", "wrong": "tides"},
]

_last_context = ""  # Global variable to store the last context


@function_tool
def search_knowledge_by_keyword(query: str) -> dict:
    """
    Search the knowledge database for relevant facts.
    param query: The single keyword query string to search for.
    """
    global _last_context
    matches = [doc for doc in _special_knowledge_db if query.lower() in doc.lower()]
    print(f"Found {len(matches)} matches for '{query}'")
    _last_context = "\n".join(matches)
    return {"status": "ok", "context": _last_context}


agent = Agent(
    name="RAG Agent",
    instructions="""
You are a retrieval-augmented knowledge agent.
Break down the user's query into smaller parts if needed
to fetch relevant context for the user's query.
""",
    tools=[search_knowledge_by_keyword],
    model="gpt-4o",  # Specify the model to use
)


@function_tool
def get_last_context() -> str:
    """
    Retrieve the last context used by the grounding agent.
    """
    global _last_context
    if not _last_context:
        return "No context available."
    return _last_context


class GroundedAnswer(BaseModel):
    """Output model for grounding agent."""

    is_answer_grounded: bool
    feedback: str


grounding_agent = Agent(
    name="Grounding Agent",
    instructions="""
You are a grounding agent.
Your task is to evaluate the correctness of answers
based on the provided question, context used,
and output answer.
""",
    model="gpt-4o",  # Specify the model to use
    output_type=GroundedAnswer,
    tools=[get_last_context],
)


for benchmark in _benchmarks:
    question = benchmark["q"]
    answer = benchmark["a"]
    wrong_answer = benchmark["wrong"]
    result = asyncio.run(Runner.run(agent, input=question)).final_output.strip()
    grounding_input = dict(
        question=question,
        answer=result,
    )
    print("" + "=" * 40)
    grounding = asyncio.run(
        Runner.run(grounding_agent, input=str(grounding_input))
    ).final_output
    print(f"Grounded: {grounding.is_answer_grounded}")
    print(f"Feedback: {grounding.feedback}")
    print(f"Question: {question}")
    print(f"Answer: {result}")
