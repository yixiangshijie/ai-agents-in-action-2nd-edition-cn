import asyncio

from agents import Agent, Runner, function_tool

# In-memory journal state (list of entries)
_journal = []


@function_tool
def record_event(entry: str) -> dict:
    """Add a new travel event to the journal."""
    _journal.append(entry)
    print(f"Event recorded: {entry}")
    return {"status": "recorded", "entry": entry}


@function_tool
def load_journal() -> dict:
    """Load the current travel journal entries."""
    print("Loading journal entries...")
    return {"status": "loaded", "journal": "\n".join(_journal)}


agent = Agent(
    name="Time Tracker Agent",
    instructions="""You are a time tracking journaling agent.
Always use the 'load_journal' tool at the start to get past entries.
For a new event, call 'record_event' to save it.
If asked for a summary or to show the journal, output all recorded events.""",
    tools=[record_event, load_journal],
)

# Simulate a series of historical travel events
travel_events = [
    "Traveled to Ancient Rome and watched a gladiator fight",
    "Visited the signing of the Declaration of Independence in 1776",
    "Witnessed the moon landing in 1969",
]


async def main():
    print("Recording travels:")
    for event in travel_events:
        await Runner.run(agent, event)
    # Ask the agent to summarize the adventures
    result = await Runner.run(agent, "Show my travel history")
    print("\nFinal Journal:")
    print(result.final_output)


asyncio.run(main())
