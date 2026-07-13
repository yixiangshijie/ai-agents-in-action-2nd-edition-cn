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
    iteration_count: int = 0
    active_signal: AttentionSignal = AttentionSignal.NONE


class GateDecision(str, Enum):
    PRESENT = "present"                # Safe to present the response
    GATHER_MORE = "gather_more"        # Borderline, gather more info
    SIGNAL_UNCERTAINTY = "signal_uncertainty"  # Not confident enough


def check_confidence_gate(workspace: CognitiveWorkspace) -> GateDecision:
    # Hard threshold: never present below 0.3
    if workspace.confidence < 0.3:
        return GateDecision.SIGNAL_UNCERTAINTY

    # Soft threshold: try gathering more if between 0.3 and 0.6
    if workspace.confidence < 0.6:
        # Only try gathering more if we have iteration budget remaining
        if workspace.iteration_count < 3:
            return GateDecision.GATHER_MORE
        return GateDecision.SIGNAL_UNCERTAINTY

    # Check for unresolved contradictions
    if workspace.active_signal == AttentionSignal.CONTRADICTION:
        return GateDecision.GATHER_MORE

    # Check confidence trend: declining confidence is a red flag
    if len(workspace.confidence_trend) >= 3:
        recent = workspace.confidence_trend[-3:]
        # Three consecutive confidence drops means something is wrong
        if all(recent[i] > recent[i + 1] for i in range(2)):
            return GateDecision.GATHER_MORE

    return GateDecision.PRESENT


# --- Demo ---
if __name__ == "__main__":
    # Test case 1: High confidence, should present
    ws1 = CognitiveWorkspace(
        raw_query="Simple lookup",
        confidence=0.85,
        confidence_trend=[0.5, 0.65, 0.75, 0.85],
    )
    print(f"Test 1 (high confidence): "
          f"{check_confidence_gate(ws1).value}")

    # Test case 2: Low confidence, should signal uncertainty
    ws2 = CognitiveWorkspace(
        raw_query="Unknown domain",
        confidence=0.2,
        iteration_count=5,
    )
    print(f"Test 2 (low confidence): "
          f"{check_confidence_gate(ws2).value}")

    # Test case 3: Borderline with budget remaining
    ws3 = CognitiveWorkspace(
        raw_query="Partial info",
        confidence=0.45,
        iteration_count=1,
    )
    print(f"Test 3 (borderline, budget left): "
          f"{check_confidence_gate(ws3).value}")

    # Test case 4: Declining confidence trend
    ws4 = CognitiveWorkspace(
        raw_query="Getting worse",
        confidence=0.65,
        confidence_trend=[0.8, 0.75, 0.7, 0.65],
    )
    print(f"Test 4 (declining trend): "
          f"{check_confidence_gate(ws4).value}")
