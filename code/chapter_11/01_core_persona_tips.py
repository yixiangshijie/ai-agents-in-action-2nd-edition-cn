from datetime import date

from agents import Agent, Runner
from pydantic import BaseModel, Field


class Answer(BaseModel):  # A
    """Machine-readable answer format."""

    answer: str = Field(..., description="Concise, user-facing answer")
    citations: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)


def core_instructions(ctx, agent) -> str:  # B
    today = date.today().isoformat()  # C
    return (
        f"You are SupportMentor, a helpful domain assistant. Today is {today}.\n"  # D
        "Always:\n"
        "1) Answer concisely; 2) Prefer retrieved context; 3) If context is missing, say you don't know.\n"
        "Output must be valid JSON matching the Answer schema.\n"
        "Never: make policy exceptions or invent facts."
    )


core_agent = Agent(
    name="SupportMentor", instructions=core_instructions, output_type=Answer
)

input = "What's our refund window for accessories?"
result = Runner.run_sync(core_agent, input)
print(result.final_output)
