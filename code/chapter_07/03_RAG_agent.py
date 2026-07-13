import asyncio

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

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


@function_tool
def search_knowledge_by_keyword(query: str) -> dict:
    """
    Search the knowledge database for relevant facts.
    param query: The single keyword query string to search for.
    """
    matches = [doc for doc in _special_knowledge_db if query.lower() in doc.lower()]
    print(f"Found {len(matches)} matches for '{query}'")
    return {"status": "ok", "context": "\n".join(matches)}


agent = Agent(
    name="RAG Agent",
    instructions="""
You are a retrieval-augmented knowledge agent.
Break down the user's query into smaller parts if needed
to fetch relevant context for the user's query.
Always answer with a single word.
""",
    tools=[search_knowledge_by_keyword],
    model="gpt-4o",  # Specify the model to use
)

for benchmark in _benchmarks:
    question = benchmark["q"]
    answer = benchmark["a"]
    wrong_answer = benchmark["wrong"]
    result = asyncio.run(Runner.run(agent, input=question)).final_output.strip()
    print("" + "=" * 40)
    print(f"Question: {question}")
    print(f"Answer: {result}")
    if result.lower() == answer.lower():
        print(f"Correct -> {answer}")
    else:
        print(f"Incorrect -> Expected: {answer}")
        if wrong_answer:
            print(f"Wrong answer was: {wrong_answer}")
