import asyncio

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStdio


@function_tool
def travel_back(year: int, years: int) -> str:
    """
    Travel back in time by a given number of years from the start year.
    """
    print(f"Time travel back by {years} years")
    return f"Current year in time: {year - years}"


@function_tool
def travel_forward(year: int, years: int) -> str:
    """Travel forward in time by a given number of years from the start year."""
    print(f"Time travel forward by {years} years")
    return f"Current year in time: {year - years}"


@function_tool
def how_correct_is_answer(days_in_the_past: int) -> str:
    """
    Returns how many days away from the correct answer the provided answer is.
    If the answer is correct, returns a confirmation message.
    """
    correct_days = 26  # The correct answer is 26 days
    diff = days_in_the_past - correct_days
    if diff == 0:
        answer = "Correct answer!"
    else:
        answer = f"{diff:+d} days away from the correct answer."
    print(f"Answer is {answer}")
    return answer


async def main():
    thinking_srv = MCPServerStdio(
        name="sequential-thinking",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        },
    )

    instructions = """
You are a time travel assistant. 
You have tools 'travel_back' and 'travel_forward' to perform time jumps. 
First, think step-by-step about the problem to devise a plan.
You must use the tools to calculate dates. 
After using a tool, reflect on the result and continue reasoning. 
Consider braching out your reasoning into multiple branches if necessary.
Execute and consider each branch step-by-step.
Check the answer is correct using 'how_correct_is_answer' tool.
If the answer is correct (0 days) provide the final answer and plan.
If the answer is not correct, continue reasoning and try to find the correct answer.
    """
    agent = Agent(
        model="o3",
        name="Time Travel Agent",
        instructions=instructions,
        tools=[
            travel_back,
            travel_forward,
            how_correct_is_answer,
        ],
        mcp_servers=[thinking_srv],
    )

    async with thinking_srv:
        time_travel_problem = """
In a sci-fi film, Alex is a time traveler who decides to go back in time
to witness a famous historical event that took place 125 years ago,
which lasted for 10 days. He arrives three days before the event starts.
However, after spending six days in the past, he jumps forward in time
by 50 years and stays there for 20 days. Then, he travels back to
witness the end of the end. Alex current year is 2050.
How many days does Alex spend in the past before he sees the end of the event?
"""
        print("Running...")
        result = await Runner.run(
            agent,
            time_travel_problem,
            max_turns=25,
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
