from pydantic import BaseModel, Field


class SubTopic(BaseModel):
    """A single sub-topic within the research plan."""
    name: str
    status: str = "pending"  # pending | in_progress | complete
    notes: str = ""


class ResearchPlan(BaseModel):
    """Strategic plan that guides the research process."""
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
            findings=self.findings,
            sources=self.sources_consulted,
            pending_questions=self.follow_up_questions,
            plan=self.plan.to_context(),
            iteration=self.iteration_count,
            remaining=self.max_iterations - self.iteration_count,
        ))
