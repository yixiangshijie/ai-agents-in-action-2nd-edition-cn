from pydantic import BaseModel, Field
from enum import Enum


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


def route_attention(workspace: CognitiveWorkspace) -> str:
    """Read workspace signals and determine next module."""

    # System 1 fast path: bypass full cognitive cycle for simple,
    # familiar problems
    if (workspace.complexity_estimate < 0.3
        and workspace.memory_hits
            and workspace.active_signal == AttentionSignal.NONE):
        return "FAST_RESPOND"

    # Signal-driven routing
    if workspace.active_signal == AttentionSignal.TASK_COMPLETE:
        return "RESPOND"

    if workspace.active_signal == AttentionSignal.STAGNATION:
        # Meta-planning records the failed strategy to prevent repetition
        workspace.failed_approaches.append(
            workspace.current_strategy.value
        )
        return "META_PLAN"

    if workspace.active_signal == AttentionSignal.CONTRADICTION:
        # Override the current strategy when contradictions are detected
        workspace.current_strategy = StrategyType.HYPOTHESIS_TEST
        return "PLAN"

    if workspace.active_signal == AttentionSignal.LOW_CONFIDENCE:
        if workspace.confidence < 0.2:
            # Below minimum confidence threshold, surface uncertainty
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
