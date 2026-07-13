import asyncio

from agents import Agent, Runner

# Define an agent that always explains its reasoning step by step
cot_agent = Agent(
    name="TimeTravelerCoT",
    instructions=(
        "You are a time travel problem solver. "
        "Work out the solution step by step, then give the final answer."
    ),
)

# Example time travel question
question = (
    "Starting in 2025, you travel 10 years to the past, then 5 years to the future. "
    "What year do you end up in?"
)

# Run the agent (using await in an async context, or Runner.run_sync in a script)
result = asyncio.run(Runner.run(cot_agent, input=question))
print(result.final_output)
