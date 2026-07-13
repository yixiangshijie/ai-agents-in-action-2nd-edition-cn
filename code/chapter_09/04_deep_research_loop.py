import asyncio
import os
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agents.mcp import MCPServerStdio


class SubTopic(BaseModel):
    name: str
    status: str = "pending"
    notes: str = ""


class ResearchPlan(BaseModel):
    sub_topics: list[SubTopic] = Field(default_factory=list)
    strategy_notes: str = ""

    def to_context(self) -> str:
        return str(dict(
            sub_topics=[
                dict(name=st.name, status=st.status, notes=st.notes)
                for st in self.sub_topics
            ],
            strategy_notes=self.strategy_notes,
        ))

    @property
    def progress_summary(self) -> str:
        if not self.sub_topics:
            return "No plan yet"
        total = len(self.sub_topics)
        complete = sum(1 for st in self.sub_topics
                       if st.status == "complete")
        in_progress = sum(1 for st in self.sub_topics
                          if st.status == "in_progress")
        return (f"{complete}/{total} complete, "
                f"{in_progress} in progress")


class ResearchState(BaseModel):
    goal: str = ""
    findings: list[str] = Field(default_factory=list)
    sources_consulted: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    plan: ResearchPlan = Field(default_factory=ResearchPlan)
    iteration_count: int = 0
    max_iterations: int = 10
    status: str = "in_progress"

    @property
    def should_continue(self) -> bool:
        return (
            self.status == "in_progress"
            and self.iteration_count < self.max_iterations
            and len(self.follow_up_questions) > 0
        )

    def to_context(self) -> str:
        return str(dict(
            goal=self.goal,
            findings=self.findings[-5:],
            sources=self.sources_consulted,
            pending_questions=self.follow_up_questions,
            plan=self.plan.to_context(),
            iteration=self.iteration_count,
            remaining=self.max_iterations - self.iteration_count,
        ))


class SubTopicUpdate(BaseModel):
    name: str
    status: str
    notes: str = ""


class ResearchIteration(BaseModel):
    summary_of_findings: str
    sources_used: list[str]
    follow_up_questions: list[str]
    goal_satisfied: bool
    confidence: float
    reasoning: str
    plan_updates: list[SubTopicUpdate] = []
    new_sub_topics: list[SubTopicUpdate] = []
    strategy_notes: str = ""


research_agent = Agent(
    name="Deep Research Agent",
    instructions="""
You are a deep research agent.
Your goal is to thoroughly research a topic by searching for
information, reading results, and synthesizing findings.

RESEARCH PLAN:
- On your FIRST iteration (when no plan exists yet), analyze the
  research goal and create a plan by returning sub-topics in
  new_sub_topics. Each sub-topic should be a distinct aspect of
  the goal. Set status to "pending" for unstarted topics and
  "in_progress" for the one you are currently researching.
- On SUBSEQUENT iterations, update existing sub-topics via
  plan_updates (change status to "in_progress" or "complete",
  add notes summarizing what was learned). You may also add
  new sub-topics via new_sub_topics if you discover the research
  requires areas not in the original plan.
- Use strategy_notes to record high-level observations about
  your research approach or adjustments to strategy.

Each iteration, review your plan and accumulated state, identify
gaps, search for new information, and update your findings.
follow_up_questions should contain specific search queries for
the next iterations. The plan provides strategic direction while
follow_up_questions drive tactical execution.

When you believe you have sufficient information to answer
the research goal comprehensively, set goal_satisfied to true.
""",
    model="gpt-4o",
    output_type=ResearchIteration,
)


def apply_plan_updates(
    plan: ResearchPlan, iteration: ResearchIteration
) -> None:
    """Apply plan changes from an iteration to the mutable plan."""
    existing = {st.name: st for st in plan.sub_topics}
    for update in iteration.plan_updates:
        if update.name in existing:
            existing[update.name].status = update.status
            if update.notes:
                existing[update.name].notes = update.notes

    for new_st in iteration.new_sub_topics:
        if new_st.name not in existing:
            plan.sub_topics.append(
                SubTopic(
                    name=new_st.name,
                    status=new_st.status,
                    notes=new_st.notes,
                )
            )

    if iteration.strategy_notes:
        plan.strategy_notes = iteration.strategy_notes


async def run_research_loop(
    goal: str, max_iterations: int = 10
) -> ResearchState:
    search_server = MCPServerStdio(
        name="Brave Search",
        params={
            "command": "npx",
            "args": ["-y", "@anthropic/brave-search-mcp"],
            "env": {"BRAVE_API_KEY": os.environ["BRAVE_API_KEY"]},
        },
    )
    async with search_server:
        agent = research_agent.clone(
            mcp_servers=[search_server]
        )
        state = ResearchState(
            goal=goal,
            max_iterations=max_iterations,
            follow_up_questions=[goal],
        )

        while state.should_continue:
            state.iteration_count += 1
            question = state.follow_up_questions.pop(0)
            input_context = dict(
                current_question=question,
                accumulated_state=state.to_context(),
                research_plan=state.plan.to_context(),
            )
            print(f"\n--- Iteration {state.iteration_count} ---")
            print(f"Investigating: {question}")

            result = await Runner.run(
                agent, input=str(input_context)
            )
            iteration = result.final_output

            state.findings.append(iteration.summary_of_findings)
            state.sources_consulted.extend(iteration.sources_used)
            state.follow_up_questions.extend(
                iteration.follow_up_questions
            )
            apply_plan_updates(state.plan, iteration)

            if iteration.goal_satisfied:
                state.status = "complete"
                print(f"Goal satisfied (confidence: "
                      f"{iteration.confidence:.0%})")

            print(f"Found: {iteration.summary_of_findings[:100]}...")
            print(f"New questions: {len(iteration.follow_up_questions)}")
            print(f"Plan: {state.plan.progress_summary}")

        return state


async def main():
    state = await run_research_loop(
        goal="What are the latest advances in solid-state batteries "
             "and which companies are leading commercialization?",
        max_iterations=8,
    )
    print(f"\n{'='*50}")
    print(f"Research complete after {state.iteration_count} iterations")
    print(f"Sources consulted: {len(state.sources_consulted)}")
    print(f"Status: {state.status}")
    print(f"Plan progress: {state.plan.progress_summary}")
    if state.plan.sub_topics:
        for st in state.plan.sub_topics:
            print(f"  [{st.status}] {st.name}")
    for i, finding in enumerate(state.findings, 1):
        print(f"\nFinding {i}: {finding[:200]}...")


asyncio.run(main())
