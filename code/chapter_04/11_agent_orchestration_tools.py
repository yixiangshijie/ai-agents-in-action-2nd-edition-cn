import asyncio
import os
from pathlib import Path
from typing import List

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel

SANDBOX = os.path.dirname(os.path.abspath(__file__))
SCRIPT = Path(__file__).with_name("04_research_tools_mcp_server.py").resolve()

research_srv = MCPServerStdio(
    name="Research Tools",
    params=MCPServerStdioParams(
        command="mcp",
        args=["run", str(SCRIPT)],
    ),
)
thinking_srv = MCPServerStdio(
    name="sequential-thinking",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
    },
)
fs_srv = MCPServerStdio(
    name="filesystem",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", SANDBOX],
    },
)


class ResearchSourcesModel(BaseModel):
    research_sources: List[str]
    """A list of research sources to use for research."""


@function_tool
async def research_agent(instructions: str) -> ResearchSourcesModel:
    """
    Use the research agent to find research sources.
    """
    agent = Agent(
        name="Research Agent",
        instructions="""
You are a research assistant.
Your role is to find research sources.
Never make up or invent any research sources.
""",
        output_type=ResearchSourcesModel,
        mcp_servers=[research_srv],
    )
    async with research_srv:
        result = await Runner.run(agent, instructions)
        return result.final_output


@function_tool
async def filesystem_agent(instructions: str) -> str:
    """
    Use the filesystem agent to read or write files.
    """
    agent = Agent(
        name="Filesystem Agent",
        instructions="""
You are a filesystem assistant.
Your role is to read and write files.
Never make up or invent any ouput.
""",
        mcp_servers=[fs_srv],
    )
    async with fs_srv:
        result = await Runner.run(agent, instructions)
        return result.final_output


orchestration_agent = Agent(
    name="Orchestration Agent",
    instructions="""
You are a research planning and orchestration assistant.
Your role is to plan the research, find existing research already done and update it.
Use the research agent to find research sources.
Use the sequentialThinking tool to create a research plan based on the sources.
Use the filesystem agent to help find existing research and update it.
Use the filesystem agent to write the output as a text file.
""",
    tools=[research_agent, filesystem_agent],
)


async def main():
    async with thinking_srv:
        goal = """
Produce a research plan to find the book 'The Hitchhiker's Guide to the Galaxy'
"""
        orchestration_agent.mcp_servers = [thinking_srv]
        print("Running...", goal)
        result = await Runner.run(
            orchestration_agent,
            goal,
            max_turns=25,
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
