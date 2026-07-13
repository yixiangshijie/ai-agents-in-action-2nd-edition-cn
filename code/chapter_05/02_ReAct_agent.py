import asyncio

from agents import Agent, Runner, function_tool


# Define two tools for time calculations
@function_tool
def travel_back(year: int, years: int) -> int:
    """Travel back in time by a given number of years from the start year."""
    return year - years


@function_tool
def travel_forward(year: int, years: int) -> int:
    """Travel forward in time by a given number of years from the start year."""
    return year + years


# Create an agent equipped with the tools
react_agent = Agent(
    name="TimeTravelerReAct",
    instructions=(
        "You are a time travel assistant. You have tools 'travel_back' and 'travel_forward' to perform time jumps. "
        "First, think step-by-step about the problem. If needed, use the tools to calculate dates. "
        "After using a tool, reflect on the result and continue reasoning. "
        "After gathering information, provide the final answer."
    ),
    tools=[travel_back, travel_forward],
)

# A time travel problem that requires using the tools
problem = (
    "I am in the year 2050."
    "I travel 25 years back in time, then travel 10 years forward, "
    "and finally go 5 years back again. What year is it now?"
)

result = asyncio.run(Runner.run(react_agent, input=problem))
print(result.final_output)
