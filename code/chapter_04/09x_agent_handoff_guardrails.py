import asyncio
import os
from pathlib import Path
from typing import List

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    handoff,
    output_guardrail,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel

SANDBOX = os.path.dirname(os.path.abspath(__file__))
SCRIPT = Path(__file__).with_name("04_research_tools_mcp_server.py").resolve()


class ResearchPlanModel(BaseModel):
    """Output model for the research plan."""

    research_plan: str
    """The final research plan as text."""
    research_plan_file: str
    """The path to the research plan file."""
    is_sufficiently_detailed: bool
    """Flag to indicate if the research plan is sufficiently detailed."""


class ResearchPlanGuardrailModel(BaseModel):
    """Model for the research plan guardrail output."""

    feedback: str
    """Feedback on the research plan."""
    is_sufficiently_detailed: bool
    """Flag to indicate if the research plan is sufficiently detailed."""


research_plan_guardrail_agent = Agent(
    name="Research Plan Guardrail Agent",
    instructions="""
You are an output guardrail agent.
Confirm the research plan is sufficiently detailed, atleast 1000 characters in length.
If it is not sufficiently detailed, flag it and provide feedback.
""",
    output_type=ResearchPlanModel,
)


@output_guardrail
async def research_plan_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: ResearchPlanModel
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        research_plan_guardrail_agent, output.research_plan, context=ctx.context
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_sufficiently_detailed,
    )


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
        output_type=ResearchPlanModel,
        output_guardrails=[research_plan_guardrail],
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
        # configure agent structure and mcp servers
        research_agent.mcp_servers = [research_srv]
        research_agent.handoffs = [thinking_agent]
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
