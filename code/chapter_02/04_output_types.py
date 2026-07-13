
from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel

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

class ResearchPlanModel(BaseModel):
    tasks: dict[int, str]
    """A list of tasks to perform for research."""

    
agent = Agent(
    name="Research Planner", 
    instructions=instructions,
    output_type=ResearchPlanModel,
    )

input = "learn about AI agents"

result = Runner.run_sync(
    agent, 
    input=input,
    )

print(result.final_output)