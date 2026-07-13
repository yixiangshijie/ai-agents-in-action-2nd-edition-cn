from agents import Agent, ModelSettings, Runner
from dotenv import load_dotenv

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

agent = Agent(
    name="Research Planner", 
    instructions=instructions,
    model="gpt-4.1",  # Specify the model to use
    model_settings=ModelSettings(
        temperature=0.0,  # Set the temperature for repeatability
        max_tokens=150,  # Set the maximum number of tokens in the response
        top_p=1.0,  # Set the top-p sampling parameter
        frequency_penalty=0.5,  # Set the frequency penalty
        presence_penalty=0.5,  # Set the presence penalty
    )
)

input = "learn about AI agents"

result = Runner.run_sync(
    agent, 
    input=input,
    )

print(result.final_output)
