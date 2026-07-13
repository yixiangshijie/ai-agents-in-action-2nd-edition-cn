import asyncio
import os
from pathlib import Path
from typing import List

from agents import Agent, RunContextWrapper, Runner, handoff
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel

SANDBOX = os.path.dirname(os.path.abspath(__file__))
SCRIPT = Path(__file__).with_name("04_research_tools_mcp_server.py").resolve()


async def main():
    class ResearchSourcesModel(BaseModel):
        research_sources: List[str]
        """A list of research sources to use for research."""

    # Instantiate the agents first…
    research_agent = Agent(
        name="Research Agent",
        output_type=ResearchSourcesModel,
        instructions="""
You are a research assistant.
Your role is to find research sources. 
Do not make up or invent any research sources.
Always hand off to the thinking agent.
""",
    )
    thinking_agent = Agent(
        name="Thinking Agent",
        instructions="""
You are a research planning assistant.
Your role is to plan the research.
You will receive a list of research sources from the research agent.
Use the sequentialThinking tool to create a research plan based on the sources.
Always hand off to the filesystem agent.
""",
    )
    filesystem_agent = Agent(
        name="Filesystem Agent",
        instructions="""
You are a filesystem assistant.
Your role is to write the output as a text file.
Never make up or invent any ouput.
""",
    )
    # Instantiate the servers next…
    servers = [
        MCPServerStdio(
            name="Research Tools",
            params=MCPServerStdioParams(
                command="mcp",
                args=["run", str(SCRIPT)],
            ),
        ),
        MCPServerStdio(
            name="sequential-thinking",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            },
        ),
        MCPServerStdio(
            name="filesystem",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", SANDBOX],
            },
        ),
    ]

    # …then open them all at once
    async with (
        servers[0] as research_srv,
        servers[1] as thinking_srv,
        servers[2] as fs_srv,
    ):
        goal = """
Produce a research plan to find the book 'The Hitchhiker's Guide to the Galaxy'
"""

        async def research_handoff(
            ctx: RunContextWrapper[None],
            sources: ResearchSourcesModel,
        ):
            print(f"Thinking agent called with sources: {sources.research_sources}")
            # we could implement other processing here

        # configure agent structure and mcp servers
        research_agent.mcp_servers = [research_srv]
        agent_handoff = handoff(
            agent=thinking_agent,
            on_handoff=research_handoff,
            input_type=ResearchSourcesModel,
        )
        research_agent.handoffs = [agent_handoff]
        thinking_agent.mcp_servers = [thinking_srv]
        thinking_agent.handoffs = [filesystem_agent]
        filesystem_agent.mcp_servers = [fs_srv]

        print("Running...", goal)
        result = await Runner.run(
            research_agent,
            goal,
            max_turns=25,
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
