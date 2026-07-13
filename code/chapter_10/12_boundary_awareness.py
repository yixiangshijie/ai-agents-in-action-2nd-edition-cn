from pydantic import BaseModel, Field
from enum import Enum


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
    confidence: float = 0.5
    findings: list[Finding] = Field(default_factory=list)
    memory_hits: list[str] = Field(default_factory=list)
    active_signal: AttentionSignal = AttentionSignal.NONE


class KnowledgeBoundary(str, Enum):
    WITHIN = "within_knowledge"
    EDGE = "edge_of_knowledge"
    OUTSIDE = "outside_knowledge"


def assess_knowledge_boundary(
    workspace: CognitiveWorkspace,
) -> KnowledgeBoundary:
    signals = []

    # Check retrieval quality
    if workspace.findings:
        avg_relevance = sum(
            f.relevance_score for f in workspace.findings
        ) / len(workspace.findings)
        signals.append(avg_relevance)
    else:
        # No findings at all is a strong signal we are outside
        # known territory
        signals.append(0.0)

    # Check memory coverage
    if workspace.memory_hits:
        # Memory hits suggest the agent has seen related problems
        signals.append(0.8)
    else:
        signals.append(0.2)

    # Check confidence state
    signals.append(workspace.confidence)

    avg_signal = sum(signals) / len(signals)

    if avg_signal > 0.6:
        return KnowledgeBoundary.WITHIN
    elif avg_signal > 0.3:
        return KnowledgeBoundary.EDGE
    else:
        workspace.active_signal = AttentionSignal.LOW_CONFIDENCE
        return KnowledgeBoundary.OUTSIDE


# --- Demo ---
if __name__ == "__main__":
    # Test case 1: Within knowledge (good findings, memory, confidence)
    ws1 = CognitiveWorkspace(
        raw_query="Known domain query",
        confidence=0.8,
        findings=[
            Finding(content="Relevant result",
                    source="docs", relevance_score=0.9),
        ],
        memory_hits=["Past experience with similar issue"],
    )
    print(f"Test 1 (within): "
          f"{assess_knowledge_boundary(ws1).value}")

    # Test case 2: Edge of knowledge (some findings, no memory)
    ws2 = CognitiveWorkspace(
        raw_query="Partially known query",
        confidence=0.4,
        findings=[
            Finding(content="Partial result",
                    source="blog", relevance_score=0.5),
        ],
    )
    print(f"Test 2 (edge): "
          f"{assess_knowledge_boundary(ws2).value}")

    # Test case 3: Outside knowledge (no findings, no memory, low conf)
    ws3 = CognitiveWorkspace(
        raw_query="Completely unknown domain",
        confidence=0.2,
    )
    result3 = assess_knowledge_boundary(ws3)
    print(f"Test 3 (outside): {result3.value}, "
          f"signal={ws3.active_signal.value}")
