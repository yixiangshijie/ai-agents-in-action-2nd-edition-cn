import asyncio
import os
from pathlib import Path

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel

SANDBOX = os.path.dirname(os.path.abspath(__file__))
SCRIPT = Path(__file__).with_name("01_research_tools_mcp_server.py").resolve()


class ResearchOutputModel(BaseModel):
    """Output model for the research agent."""

    research_plan: str
    """The final research plan as text."""
    research_plan_file: str
    """The path to the research plan file."""


@input_guardrail
async def research_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    forbidden_research = "The Hitchhiker's Guide to the Galaxy"
    if forbidden_research in input:
        research_forbidden = True
    else:
        research_forbidden = False

    return GuardrailFunctionOutput(
        output_info=f"user asked: {input}",
        tripwire_triggered=research_forbidden,
    )


@output_guardrail
async def research_output_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: ResearchOutputModel
) -> GuardrailFunctionOutput:
    if len(output.research_plan) < 100:
        insufficient_research = True
    else:
        insufficient_research = False

    return GuardrailFunctionOutput(
        output_info="research plan length: {len(output.research_plan)}",
        tripwire_triggered=insufficient_research,
    )


async def main():
    # Instantiate the servers first…
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

    instructions = """
You are a research assistant who can use tools to perform and plan research.
Given a research goal, use the research tools to find research sources.
Then, use the sequential thinking tool to plan the research.
Finally, use the filesystem tool to write the research plan as a text file.
    """

    # …then open them all at once
    async with (
        servers[0] as research_srv,
        servers[1] as thinking_srv,
        servers[2] as fs_srv,
    ):
        agent = Agent(
            name="Assistant",
            instructions=instructions,
            mcp_servers=[research_srv, thinking_srv, fs_srv],
            output_type=ResearchOutputModel,
            input_guardrails=[research_guardrail],
            output_guardrails=[research_output_guardrail],
        )
        goal = """
Produce a research plan to find the book 'The Hitchhiker's Guide to the Galaxy'
"""
        try:
            print("Running...", goal)
            result = await Runner.run(agent, goal)
            print(result.final_output)
        except InputGuardrailTripwireTriggered as input_tripped:
            print(f"""
Input guardrail tripwire triggered: 
{input_tripped.guardrail_result.output.output_info}
""")
        except OutputGuardrailTripwireTriggered as output_tripped:
            print(f"""
Output guardrail tripwire triggered: 
{output_tripped.guardrail_result.output.output_info}
""")
            print("Done")


if __name__ == "__main__":
    asyncio.run(main())
