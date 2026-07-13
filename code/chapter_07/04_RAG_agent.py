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
""",
    tools=[search_knowledge_by_keyword],
    model="gpt-4o",  # Specify the model to use
)


class EvaluationOutput(BaseModel):
    """Output model for evaluation agent."""

    is_correct: bool
    feedback: str


evaluation_agent = Agent(
    name="Evaluation Agent",
    instructions="""
You are an evaluation agent.
Your task is to evaluate the answers provided by the RAG Agent.
You will compare the answer against 
the expected answers key term to validate correctness.
""",
    output_type=EvaluationOutput,
)

for benchmark in _benchmarks:
    question = benchmark["q"]
    answer = benchmark["a"]
    wrong_answer = benchmark["wrong"]
    result = asyncio.run(Runner.run(agent, input=question)).final_output.strip()
    evaluation_input = dict(
        question=question,
        answer=result,
        expected_key_term=answer,
        wrong_answer=wrong_answer,
    )
    print("" + "=" * 40)
    evaluation = asyncio.run(
        Runner.run(evaluation_agent, input=str(evaluation_input))
    ).final_output
    print(f"Evaluation: {evaluation.is_correct}")
    print(f"Feedback: {evaluation.feedback}")
    print(f"Question: {question}")
    print(f"Answer: {result}")
    if evaluation.is_correct:
        print(f"Correct -> {answer}")
    else:
        print(f"Incorrect -> Expected: {answer}")
        if wrong_answer:
            print(f"Wrong answer was: {wrong_answer}")
