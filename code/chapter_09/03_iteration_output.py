from pydantic import BaseModel


class SubTopicUpdate(BaseModel):
    """An update to a single sub-topic in the plan."""
    name: str
    status: str  # pending | in_progress | complete
    notes: str = ""


class ResearchIteration(BaseModel):
    """Output from a single research iteration."""
    summary_of_findings: str
    sources_used: list[str]
    follow_up_questions: list[str]
    goal_satisfied: bool
    confidence: float
    reasoning: str
    plan_updates: list[SubTopicUpdate] = []
    new_sub_topics: list[SubTopicUpdate] = []
    strategy_notes: str = ""
