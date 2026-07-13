from agents import Agent, Runner, trace
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

# Load environment variables from .env file
load_dotenv()

# Agent Instructions
instructions = """
You are a research planning assistant.

**TASK INSTRUCTIONS**
- You will be given a research topic.
- Your task is to provide a plan on how to research this topic.
- Output 5 concise tasks (5 words or less) to your plan.
"""

class Task(TypedDict):
    id: int
    description: str

class ResearchPlanModel(BaseModel):
    tasks: list[Task]
    """Numbered tasks for research."""

    model_config = ConfigDict(extra='forbid')

    
agent = Agent(
    name="Research Planner", 
    instructions=instructions,
    output_type=ResearchPlanModel,
    )

input = "learn about AI agents"

with trace("Deep Research Workflow"):
    result = Runner.run_sync(
        agent, 
        input=input,
        )

print(result.final_output)