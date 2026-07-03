"""Analysis result models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BugFinding(BaseModel):
    """One issue found during post-call evaluation."""

    title: str
    severity: str = Field(description="High | Medium | Low")
    quote: str = Field(description="Relevant quote or timestamp reference from the call")
    details: str = Field(description="What happened and what should have happened")
    criterion: str | None = Field(
        default=None,
        description="Which success criterion this relates to, if any",
    )


class EvaluationResult(BaseModel):
    """Structured output from the bug evaluator LLM."""

    call_id: str
    summary: str
    bugs: list[BugFinding] = Field(default_factory=list)
    criteria_met: list[str] = Field(default_factory=list)
    criteria_failed: list[str] = Field(default_factory=list)
