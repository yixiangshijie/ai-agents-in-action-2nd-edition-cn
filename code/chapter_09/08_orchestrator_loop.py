import asyncio
import os
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agents.mcp import MCPServerStdio


# --- Shared types (from earlier examples) ---

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
    max_iterations: int = 15
    status: str = "in_progress"

    @property
    def should_continue(self) -> bool:
        return (
            self.status == "in_progress"
            and self.iteration_count < self.max_iterations
        )

    def to_context(self) -> str:
        return str(dict(
            goal=self.goal,
            findings=self.findings[-5:],
            sources=self.sources_consulted,
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


# --- Orchestrator-specific types ---

class OrchestratorPlan(BaseModel):
    """The orchestrator's decomposition of a complex goal."""
    sub_tasks: list[SubTopic] = Field(default_factory=list)
    overall_strategy: str = ""
    current_focus: str = ""


class OrchestratorDecision(BaseModel):
    """Output from the orchestrator after evaluating progress."""
    next_action: str          # "delegate" | "re_plan" | "finalize"
    target_worker: str = ""   # which worker to delegate to
    task_description: str = ""
    reasoning: str = ""
    plan_updates: list[SubTopicUpdate] = []
    is_complete: bool = False


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


# --- Worker agents ---

research_worker = Agent(
    name="Research Worker",
    instructions="""
You are a focused research worker. You receive a specific
research sub-task and execute it thoroughly using your search
tools. Return detailed findings with sources.
Do not deviate from the assigned sub-task.
""",
    model="gpt-4o",
    output_type=ResearchIteration,
)

analysis_worker = Agent(
    name="Analysis Worker",
    instructions="""
You are a data analysis worker. You receive findings and data
to analyze. Identify patterns, contradictions, and gaps.
Return a structured analysis with confidence assessments.
""",
    model="gpt-4o",
    output_type=ResearchIteration,
)


# --- Orchestrator agent ---

orchestrator_agent = Agent(
    name="Research Orchestrator",
    instructions="""
You are a research orchestrator managing a team of workers.
Your job is to decompose complex goals, delegate sub-tasks
to the right worker, evaluate their output, and decide when
the overall goal is satisfied.

Workers available:
- Research Worker: for searching and gathering information
- Analysis Worker: for analyzing and synthesizing findings

Each iteration, review the current state and plan, then decide:
1. "delegate" - assign a sub-task to a specific worker
2. "re_plan" - revise the plan based on new information
3. "finalize" - all sub-tasks complete, ready for synthesis

Always provide reasoning for your decision.
""",
    model="gpt-4o",
    output_type=OrchestratorDecision,
)


# --- Orchestrator loop ---

async def run_orchestrator_loop(
    goal: str, max_iterations: int = 15
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
        workers = {
            "Research Worker": research_worker.clone(
                mcp_servers=[search_server]
            ),
            "Analysis Worker": analysis_worker,
        }
        state = ResearchState(
            goal=goal,
            max_iterations=max_iterations,
            follow_up_questions=[goal],
        )
        plan = OrchestratorPlan()

        for iteration in range(max_iterations):
            orch_input = dict(
                goal=state.goal,
                current_state=state.to_context(),
                plan=str(dict(
                    sub_tasks=[
                        dict(name=st.name, status=st.status,
                             notes=st.notes)
                        for st in plan.sub_tasks],
                    strategy=plan.overall_strategy,
                    focus=plan.current_focus,
                )),
                iteration=iteration + 1,
                max_iterations=max_iterations,
            )

            print(f"\n--- Orchestrator Iteration {iteration + 1} ---")
            decision = (await Runner.run(
                orchestrator_agent, input=str(orch_input)
            )).final_output

            print(f"  Action: {decision.next_action}")
            print(f"  Reasoning: {decision.reasoning[:100]}...")

            if decision.is_complete or \
               decision.next_action == "finalize":
                state.status = "complete"
                print("  Orchestrator: Goal complete.")
                break

            if decision.next_action == "delegate":
                worker = workers.get(decision.target_worker)
                if worker:
                    print(f"  Delegating to: {decision.target_worker}")
                    print(f"  Task: {decision.task_description[:80]}...")
                    worker_result = (await Runner.run(
                        worker, input=decision.task_description
                    )).final_output
                    state.findings.append(
                        worker_result.summary_of_findings
                    )
                    state.sources_consulted.extend(
                        worker_result.sources_used
                    )
                    apply_plan_updates(
                        state.plan, worker_result
                    )
                    print(f"  Worker found: "
                          f"{worker_result.summary_of_findings[:80]}...")
                else:
                    print(f"  Unknown worker: {decision.target_worker}")

            if decision.next_action == "re_plan":
                print("  Re-planning...")
                for update in decision.plan_updates:
                    existing = {st.name: st
                                for st in plan.sub_tasks}
                    if update.name in existing:
                        existing[update.name].status = \
                            update.status
                        if update.notes:
                            existing[update.name].notes = \
                                update.notes
                    else:
                        plan.sub_tasks.append(SubTopic(
                            name=update.name,
                            status=update.status,
                            notes=update.notes,
                        ))
                for st in plan.sub_tasks:
                    print(f"    [{st.status}] {st.name}")

            state.iteration_count = iteration + 1

        return state


async def main():
    state = await run_orchestrator_loop(
        goal="What are the latest advances in solid-state batteries "
             "and which companies are leading commercialization?",
        max_iterations=10,
    )
    print(f"\n{'='*50}")
    print(f"Orchestrator complete after "
          f"{state.iteration_count} iterations")
    print(f"Findings collected: {len(state.findings)}")
    print(f"Sources consulted: {len(state.sources_consulted)}")
    print(f"Status: {state.status}")
    print(f"Plan: {state.plan.progress_summary}")
    for i, finding in enumerate(state.findings, 1):
        print(f"\nFinding {i}: {finding[:200]}...")


asyncio.run(main())
