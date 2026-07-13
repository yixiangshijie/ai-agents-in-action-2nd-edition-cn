import asyncio

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

web_search_tool = ...  # WebSearchTool() or your own @function_tool
extract_tool = ...  # e.g., page extractor / cleaner
analyze_tool = ...  # e.g., code interpreter for stats

critic = Agent(name="Critic", instructions="Check completeness, bias, contradictions.")
writer = Agent(
    name="Writer", instructions="Synthesize into a concise brief with citations."
)

researcher = Agent(
    name="ResearchPlanner",
    instructions=(
        "Break down the research goal. Always use web/doc tools for facts. "
        "Track sources and avoid unsupported claims."
    ),
    tools=[
        web_search_tool,
        extract_tool,
        analyze_tool,
        critic.as_tool(),
        writer.as_tool(),
    ],
)

# Stream results to your UI
stream = Runner.run_streamed(
    researcher, "Map the 3 best open RAG rerankers and compare."
)


async def main():
    result = Runner.run_streamed(
        researcher, input="Map the 3 best open RAG rerankers and compare."
    )
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
