import asyncio
import json
from pydantic import BaseModel, Field
from enum import Enum
from agents import Agent, Runner
from agents.mcp import MCPServerStdio


# --- Cognitive Workspace (from Listing 10.1) ---

class TaskType(str, Enum):
    SIMPLE_LOOKUP = "simple_lookup"
    MULTI_STEP = "multi_step"
    CONTRADICTORY = "contradictory"
    AMBIGUOUS = "ambiguous"
    COMPOSITIONAL = "compositional"
    UNKNOWN = "unknown"


class StrategyType(str, Enum):
    DIRECT = "direct"
    DECOMPOSE = "decompose"
    EXPLORE = "explore"
    HYPOTHESIS_TEST = "hypothesis_test"


class AttentionSignal(str, Enum):
    NONE = "none"
    LOW_CONFIDENCE = "low_confidence"
    STAGNATION = "stagnation"
    CONTRADICTION = "contradiction"
    KNOWLEDGE_GAP = "knowledge_gap"
    TASK_COMPLETE = "task_complete"


class Finding(BaseModel):
    content: str
    source: str
    relevance_score: float = 0.0
    quality_note: str = ""


class CognitiveWorkspace(BaseModel):
    raw_query: str = ""
    task_type: TaskType = TaskType.UNKNOWN
    extracted_entities: list[str] = Field(default_factory=list)
    complexity_estimate: float = 0.0
    ambiguities: list[str] = Field(default_factory=list)
    current_strategy: StrategyType = StrategyType.DIRECT
    sub_goals: list[str] = Field(default_factory=list)
    alternative_strategies: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    memory_hits: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    confidence_trend: list[float] = Field(default_factory=list)
    steps_taken: list[str] = Field(default_factory=list)
    failed_approaches: list[str] = Field(default_factory=list)
    iteration_count: int = 0
    active_signal: AttentionSignal = AttentionSignal.NONE
    signal_source: str = ""


# --- Structured outputs for each module ---

class TaskRepresentation(BaseModel):
    task_type: TaskType
    extracted_entities: list[str] = Field(default_factory=list)
    complexity_estimate: float = 0.0
    ambiguities: list[str] = Field(default_factory=list)


class PlanOutput(BaseModel):
    strategy_type: StrategyType
    sub_goals: list[str] = Field(default_factory=list)
    alternative_strategies: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    progress_assessment: str
    consistency_check: bool
    confidence_delta: float
    contradictions: list[str] = Field(default_factory=list)
    recommendation: str


# --- Agents (from Listings 10.2-10.5, 10.7) ---

perception_agent = Agent(
    name="Perception",
    instructions="""You are the perception module of a cognitive agent.
    Analyze the user query and produce a structured understanding.

    Determine:
    1. task_type: simple_lookup, multi_step, contradictory, ambiguous,
       or compositional
    2. extracted_entities: Key nouns, concepts, or identifiers
    3. complexity_estimate: 0.0 (trivial) to 1.0 (highly complex)
    4. ambiguities: Anything that could be interpreted multiple ways

    A question requiring cross-referencing is at least 0.5.
    A question containing "but", "however", or "already tried" is
    likely contradictory and should be at least 0.6.

    You do NOT answer the query. You only analyze it.""",
    output_type=TaskRepresentation,
)

planning_agent = Agent(
    name="Planner",
    instructions="""You are the planning module of a cognitive agent.
    You receive a task representation and propose an execution strategy.

    Strategies:
    - DIRECT: Simple lookups, complexity < 0.3. One tool call.
    - DECOMPOSE: Multi-step problems. Break into ordered subtasks.
    - EXPLORE: Ambiguous problems. Gather information first.
    - HYPOTHESIS_TEST: Contradictory scenarios. Generate 2-3
      competing hypotheses and propose how to test each one.

    If memory_hits are present, use them to inform your strategy.

    Output: strategy_type, ordered sub_goals, alternative_strategies.""",
    output_type=PlanOutput,
)

execution_agent = Agent(
    name="Executor",
    instructions="""You are the execution module of a cognitive agent.
    You receive a specific sub-goal and execute it using available tools.

    For each result, provide:
    - content: The relevant information you found
    - source: Where it came from
    - relevance_score: 0.0 to 1.0, how relevant to the sub-goal
    - quality_note: Any quality concerns

    Be honest about quality. Metadata instead of content should get
    a low relevance_score with a quality_note explaining why.""",
    output_type=Finding,
)

evaluation_agent = Agent(
    name="Evaluator",
    instructions="""You are the evaluation module of a cognitive agent.
    After each execution step, assess quality and trajectory.

    Assess:
    1. progress_assessment: What was gained or not gained
    2. consistency_check: Are new results consistent with previous?
    3. confidence_delta: -0.3 to +0.3
    4. contradictions: Any conflicts between new and existing evidence
    5. recommendation: CONTINUE, REPLAN, ESCALATE, or TERMINATE

    Low relevance_score findings should NOT increase confidence.
    Two consecutive steps with no new info should trigger REPLAN.""",
    output_type=EvaluationResult,
)

memory_agent = Agent(
    name="Memory",
    instructions="""You are the memory module of a cognitive agent.
    You manage long-term experience using a knowledge graph.

    PROACTIVE RETRIEVAL: Use search_nodes to find relevant past
    experience. Return matching entities and observations.

    EXPERIENCE RECORDING: Record completed tasks with outcomes.
    Use create_entities for new problem types, add_observations
    for strategies and outcomes.

    RELATION BUILDING: Use create_relations when two problem
    entities share common strategies or patterns.

    Be concise. Store strategy name, outcome, and one sentence why.""",
)


# --- Attention Module (from Listing 10.6) ---

def route_attention(workspace: CognitiveWorkspace) -> str:
    """Read workspace signals and determine next module."""

    # System 1 fast path
    if (workspace.complexity_estimate < 0.3
        and workspace.memory_hits
            and workspace.active_signal == AttentionSignal.NONE):
        return "FAST_RESPOND"

    if workspace.active_signal == AttentionSignal.TASK_COMPLETE:
        return "RESPOND"

    if workspace.active_signal == AttentionSignal.STAGNATION:
        workspace.failed_approaches.append(
            workspace.current_strategy.value
        )
        return "META_PLAN"

    if workspace.active_signal == AttentionSignal.CONTRADICTION:
        workspace.current_strategy = StrategyType.HYPOTHESIS_TEST
        return "PLAN"

    if workspace.active_signal == AttentionSignal.LOW_CONFIDENCE:
        if workspace.confidence < 0.2:
            return "ESCALATE"
        return "PLAN"

    if workspace.active_signal == AttentionSignal.KNOWLEDGE_GAP:
        return "MEMORY"

    # Default cognitive cycle
    if not workspace.extracted_entities:
        return "PERCEIVE"
    if not workspace.sub_goals:
        return "PLAN"
    if (workspace.iteration_count == 0
            or workspace.active_signal == AttentionSignal.NONE):
        return "EXECUTE"

    return "EVALUATE"


# --- Workspace update helpers ---

def update_workspace_perception(workspace, result):
    output = result.final_output
    workspace.task_type = output.task_type
    workspace.extracted_entities = output.extracted_entities
    workspace.complexity_estimate = output.complexity_estimate
    workspace.ambiguities = output.ambiguities
    workspace.steps_taken.append("PERCEIVE")
    print(f"  [Perception] Type={output.task_type.value}, "
          f"Complexity={output.complexity_estimate:.2f}, "
          f"Entities={output.extracted_entities}")


def update_workspace_memory(workspace, result):
    output = result.final_output
    if isinstance(output, str) and output.strip():
        workspace.memory_hits.append(output)
    workspace.steps_taken.append("MEMORY")
    print(f"  [Memory] Hits={len(workspace.memory_hits)}")


def update_workspace_plan(workspace, result):
    output = result.final_output
    workspace.current_strategy = output.strategy_type
    workspace.sub_goals = output.sub_goals
    workspace.alternative_strategies = output.alternative_strategies
    workspace.steps_taken.append("PLAN")
    print(f"  [Planning] Strategy={output.strategy_type.value}, "
          f"Sub-goals={len(output.sub_goals)}")


def update_workspace_execution(workspace, result):
    output = result.final_output
    workspace.findings.append(output)
    if workspace.sub_goals:
        workspace.sub_goals.pop(0)
    workspace.steps_taken.append("EXECUTE")
    print(f"  [Execution] Found: {output.content[:80]}... "
          f"(relevance={output.relevance_score:.2f})")


def update_workspace_evaluation(workspace, result):
    output = result.final_output
    workspace.confidence = max(0.0, min(1.0,
        workspace.confidence + output.confidence_delta
    ))
    workspace.confidence_trend.append(workspace.confidence)

    if not output.consistency_check:
        workspace.active_signal = AttentionSignal.CONTRADICTION
        workspace.signal_source = "evaluation"

    if output.recommendation == "REPLAN":
        workspace.active_signal = AttentionSignal.STAGNATION
        workspace.signal_source = "evaluation"
    elif output.recommendation == "ESCALATE":
        workspace.active_signal = AttentionSignal.LOW_CONFIDENCE
        workspace.signal_source = "evaluation"
    elif output.recommendation == "TERMINATE":
        workspace.active_signal = AttentionSignal.TASK_COMPLETE
        workspace.signal_source = "evaluation"

    workspace.steps_taken.append("EVALUATE")
    print(f"  [Evaluation] Confidence={workspace.confidence:.2f}, "
          f"Recommendation={output.recommendation}")


# --- Response builders ---

def build_response(workspace: CognitiveWorkspace) -> str:
    findings_text = "\n".join(
        f"- {f.content} (source: {f.source}, "
        f"relevance: {f.relevance_score:.2f})"
        for f in workspace.findings
    )
    return (
        f"Query: {workspace.raw_query}\n"
        f"Strategy: {workspace.current_strategy.value}\n"
        f"Confidence: {workspace.confidence:.2f}\n"
        f"Findings:\n{findings_text}\n"
        f"Steps taken: {len(workspace.steps_taken)}"
    )


def build_uncertain_response(workspace: CognitiveWorkspace) -> str:
    return (
        f"Query: {workspace.raw_query}\n"
        f"NOTE: Low confidence ({workspace.confidence:.2f}). "
        f"The agent could not resolve this with sufficient certainty.\n"
        f"Partial findings:\n" +
        "\n".join(f"- {f.content}" for f in workspace.findings) +
        f"\nFailed approaches: {workspace.failed_approaches}\n"
        f"Suggestion: This query may require human expertise or "
        f"additional data sources."
    )


# --- Format helpers ---

def format_memory_query(workspace: CognitiveWorkspace) -> str:
    return (
        f"Search for past experience related to these entities: "
        f"{workspace.extracted_entities}. "
        f"Task type: {workspace.task_type.value}. "
        f"Query: {workspace.raw_query}"
    )


def format_planning_input(workspace: CognitiveWorkspace) -> str:
    return json.dumps({
        "task_type": workspace.task_type.value,
        "entities": workspace.extracted_entities,
        "complexity": workspace.complexity_estimate,
        "ambiguities": workspace.ambiguities,
        "memory_hits": workspace.memory_hits,
        "failed_approaches": workspace.failed_approaches,
    })


def format_execution_input(workspace: CognitiveWorkspace) -> str:
    current_goal = (workspace.sub_goals[0]
                    if workspace.sub_goals
                    else workspace.raw_query)
    return json.dumps({
        "sub_goal": current_goal,
        "context": {
            "task": workspace.raw_query,
            "strategy": workspace.current_strategy.value,
            "prior_findings": [
                f.content[:100] for f in workspace.findings[-3:]
            ],
        },
    })


def format_evaluation_input(workspace: CognitiveWorkspace) -> str:
    return json.dumps({
        "task": workspace.raw_query,
        "current_strategy": workspace.current_strategy.value,
        "latest_finding": (workspace.findings[-1].model_dump()
                           if workspace.findings else None),
        "all_findings_count": len(workspace.findings),
        "confidence": workspace.confidence,
        "confidence_trend": workspace.confidence_trend[-5:],
        "steps_taken": workspace.steps_taken[-5:],
        "remaining_sub_goals": workspace.sub_goals,
    })


# --- Experience recording ---

async def record_experience(workspace: CognitiveWorkspace):
    summary = (
        f"Task: {workspace.raw_query}\n"
        f"Type: {workspace.task_type.value}\n"
        f"Strategy: {workspace.current_strategy.value}\n"
        f"Confidence: {workspace.confidence:.2f}\n"
        f"Steps: {len(workspace.steps_taken)}\n"
        f"Failed approaches: {workspace.failed_approaches}"
    )
    print(f"  [Memory] Recording experience: "
          f"{workspace.task_type.value} -> "
          f"{workspace.current_strategy.value} "
          f"(confidence={workspace.confidence:.2f})")


# --- The Cognitive Loop (Listing 10.8) ---

async def run_cognitive_loop(
    query: str,
    max_iterations: int = 10,
    confidence_threshold: float = 0.8,
    max_cognitive_steps: int = 5,
    mcp_servers: list = None,
):
    workspace = CognitiveWorkspace(raw_query=query)

    # Attach MCP servers to execution agent if provided
    exec_agent = execution_agent
    if mcp_servers:
        exec_agent = execution_agent.clone(mcp_servers=mcp_servers)

    for i in range(max_iterations):
        workspace.iteration_count = i
        print(f"\n=== Iteration {i + 1} ===")

        # Inner cognitive cycle
        for step in range(max_cognitive_steps):
            next_module = route_attention(workspace)
            print(f"  Routing -> {next_module}")

            if next_module == "FAST_RESPOND":
                return build_response(workspace)

            if next_module == "RESPOND":
                return build_response(workspace)

            if next_module == "ESCALATE":
                return build_uncertain_response(workspace)

            if next_module == "PERCEIVE":
                result = await Runner.run(
                    perception_agent,
                    input=workspace.raw_query
                )
                update_workspace_perception(workspace, result)

            elif next_module in ("PLAN", "META_PLAN"):
                result = await Runner.run(
                    planning_agent,
                    input=format_planning_input(workspace)
                )
                update_workspace_plan(workspace, result)

            elif next_module == "MEMORY":
                # Memory module runs without MCP server in this
                # standalone demo; in production, attach memory_server
                workspace.steps_taken.append("MEMORY")
                print("  [Memory] No MCP memory server in standalone mode")
                workspace.active_signal = AttentionSignal.NONE

            elif next_module == "EXECUTE":
                result = await Runner.run(
                    exec_agent,
                    input=format_execution_input(workspace)
                )
                update_workspace_execution(workspace, result)

            elif next_module == "EVALUATE":
                result = await Runner.run(
                    evaluation_agent,
                    input=format_evaluation_input(workspace)
                )
                update_workspace_evaluation(workspace, result)

                if workspace.active_signal == AttentionSignal.TASK_COMPLETE:
                    break

            # Reset signal after processing
            workspace.active_signal = AttentionSignal.NONE

        # Check convergence at the agentic loop level
        if workspace.confidence >= confidence_threshold:
            print(f"\nConverged at confidence {workspace.confidence:.2f}")
            break

    # Record experience in memory after completion
    await record_experience(workspace)
    return build_response(workspace)


async def main():
    query = (
        "A user reports that their deployment pipeline fails "
        "intermittently, but only during high-traffic periods. "
        "The standard fix (increasing timeout thresholds) was "
        "already applied and did not resolve the issue."
    )
    print(f"Query: {query}\n")
    response = await run_cognitive_loop(query)
    print(f"\n{'='*60}")
    print("FINAL RESPONSE:")
    print(response)


asyncio.run(main())
