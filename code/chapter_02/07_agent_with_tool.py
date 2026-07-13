from agents import Agent, Runner, function_tool
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
- Begin by using the tool get_research_sources() 
to get a list of available research sources. 
- Constrain your research plan 
only to use the available research sources.
- Your task is to provide a plan for researching this topic.
- Output 5 concise tasks and specify which of the 
available research sources will be used for each task.
"""

class Task(TypedDict):
    step: int
    """Task Step."""
    research_source: str
    """The source to search."""
    description: str
    """Task description."""

class ResearchPlanModel(BaseModel):
    tasks: list[Task]
    """Numbered tasks for research."""
    model_config = ConfigDict(extra='forbid')
    

@function_tool
def get_research_sources() -> list[str]:
    """Provides a list of research sources."""
    search_sources = [
        "Wikipedia",
        "Google",
        "YouTube",
    ]
    return search_sources    
    
agent = Agent(
    name="Research Planner", 
    instructions=instructions,
    output_type=ResearchPlanModel,
    tools=[get_research_sources],  # Register the tool with the agent
    )

input = "learn about AI agents"

result = Runner.run_sync(
    agent, 
    input=input,
    )

print(result.final_output)