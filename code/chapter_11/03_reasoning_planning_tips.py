from typing import Literal

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from pydantic import BaseModel

MAX_TURNS = 3  # iteration cap

thinking_srv = MCPServerStdio(
    name="sequential-thinking",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
    },
)


class Answer(BaseModel):
    status: Literal["ok", "needs_followup"] = "ok"
    checklist: list[str] = []
    summary: str
    sources: list[str]


instructions = f"""
You are a planner-executor.
If the message starts with 'PLAN ONLY', 
return only the checklist (no actions).
1) Plan→Execute: draft a concise 3–5 item checklist, then execute.
2) ReAct: Thought→Action(tool)→Observation; 
inspect each observation before continuing.
3) Limit: stop after at most {MAX_TURNS} tool calls; 
if reached, set status='needs_followup' and return best effort.
4) Self-review: before final, catch obvious mistakes, 
ensure the question is answered, and cite sources.
Use seq_think between actions to decide the next step. 
Return Answer JSON only.
"""


async def main():
    agent = Agent(
        name="Planner",
        instructions=instructions,
        mcp_servers=[thinking_srv],
        output_type=Answer,
    )

    async with thinking_srv:
        question = "Summarize our refund policy and cite relevant internal docs."
        plan = await Runner.run(agent, f"PLAN ONLY. Question: {question}")
        print(plan.final_output.checklist)

        result = await Runner.run(agent, question)
        print(result.final_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
