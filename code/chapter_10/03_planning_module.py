from pydantic import BaseModel, Field
from enum import Enum
from agents import Agent


class StrategyType(str, Enum):
    DIRECT = "direct"
    DECOMPOSE = "decompose"
    EXPLORE = "explore"
    HYPOTHESIS_TEST = "hypothesis_test"


class PlanOutput(BaseModel):
    strategy_type: StrategyType
    sub_goals: list[str] = Field(default_factory=list)
    alternative_strategies: list[str] = Field(default_factory=list)


planning_agent = Agent(
    name="Planner",
    instructions="""You are the planning module of a cognitive agent.
    You receive a task representation from the perception module and
    propose an execution strategy.

    Select a strategy based on the task:
    - DIRECT: For simple lookups with complexity < 0.3. One tool call.
    - DECOMPOSE: For multi-step problems. Break into ordered subtasks.
      Identify which subtasks depend on others.
    - EXPLORE: For ambiguous problems. Propose information-gathering
      steps before committing to an approach.
    - HYPOTHESIS_TEST: For contradictory scenarios. Generate 2-3
      competing hypotheses and propose how to test each one.

    If memory_hits are present in the workspace, use them to inform
    your strategy. Past experience should accelerate planning, not
    replace it.

    Output a plan with: strategy_type, ordered list of sub_goals,
    and any alternative_strategies worth keeping in reserve.""",
    output_type=PlanOutput,
)
