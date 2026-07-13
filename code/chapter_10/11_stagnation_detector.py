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
    confidence_trend: list[float] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    active_signal: AttentionSignal = AttentionSignal.NONE
    signal_source: str = ""


def detect_stagnation(workspace: CognitiveWorkspace) -> bool:
    # Need at least 2 findings to compare
    if len(workspace.findings) < 2:
        return False

    # Check content overlap between last two findings
    last = workspace.findings[-1].content.lower().split()
    prev = workspace.findings[-2].content.lower().split()
    overlap = len(set(last) & set(prev)) / max(len(set(last)), 1)

    # More than 70% word overlap means the agent is finding the same things
    if overlap > 0.7:
        workspace.active_signal = AttentionSignal.STAGNATION
        workspace.signal_source = "content_overlap"
        return True

    # Check confidence plateau
    if len(workspace.confidence_trend) >= 3:
        recent = workspace.confidence_trend[-3:]
        spread = max(recent) - min(recent)
        # Confidence moving less than 0.05 across three steps
        # means no real progress
        if spread < 0.05:
            workspace.active_signal = AttentionSignal.STAGNATION
            workspace.signal_source = "confidence_plateau"
            return True

    return False


# --- Demo ---
if __name__ == "__main__":
    # Test case 1: Content overlap detected
    ws1 = CognitiveWorkspace(
        raw_query="Test query",
        findings=[
            Finding(
                content="The deployment pipeline uses timeout "
                        "thresholds to handle long-running tasks",
                source="docs",
                relevance_score=0.7,
            ),
            Finding(
                content="The deployment pipeline timeout thresholds "
                        "are used to handle long-running tasks",
                source="docs",
                relevance_score=0.6,
            ),
        ],
    )
    result1 = detect_stagnation(ws1)
    print(f"Test 1 (content overlap): stagnation={result1}, "
          f"signal={ws1.active_signal.value}")

    # Test case 2: Confidence plateau
    ws2 = CognitiveWorkspace(
        raw_query="Test query",
        confidence_trend=[0.55, 0.56, 0.55, 0.56],
        findings=[
            Finding(content="First finding about X", source="a"),
            Finding(content="Second finding about Y", source="b"),
        ],
    )
    result2 = detect_stagnation(ws2)
    print(f"Test 2 (confidence plateau): stagnation={result2}, "
          f"signal={ws2.active_signal.value}")

    # Test case 3: No stagnation (different findings)
    ws3 = CognitiveWorkspace(
        raw_query="Test query",
        confidence_trend=[0.5, 0.6, 0.75],
        findings=[
            Finding(
                content="Connection pool sizes default to 10",
                source="docs",
            ),
            Finding(
                content="Health checks run every 30 seconds "
                        "and timeout after 5 seconds",
                source="config",
            ),
        ],
    )
    result3 = detect_stagnation(ws3)
    print(f"Test 3 (no stagnation): stagnation={result3}, "
          f"signal={ws3.active_signal.value}")
