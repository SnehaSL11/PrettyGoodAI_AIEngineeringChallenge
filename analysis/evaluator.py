"""LLM bug evaluator — checks call transcript against scenario success criteria."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from analysis.models import BugFinding, EvaluationResult
from analysis.overlap_detector import build_overlap_context
from config import Settings
from patient.models import Scenario
from planning.llm import get_openai_client

logger = logging.getLogger(__name__)

EVALUATOR_SYSTEM_PROMPT = """\
You are a senior QA engineer reviewing phone calls between a patient and a medical office AI agent.

Given a test scenario (with success_criteria), a call transcript, and optional overlap signals, \
identify bugs, quality issues, or safety problems in the AI agent's behavior.

Rules:
- Focus on the AGENT's behavior, not the patient's.
- Report all the issues found in the call transcript including voice overlap issues — but not punctuation nitpicks.
- Map findings to success_criteria when possible.
- Severity: High (wrong info, safety, broken flow), Medium (poor UX, missing info), Low (minor).
- If no issues found, return an empty bugs array with an honest summary.

Voice overlap / turn-taking (report AGENT issues when evidence supports it):
- Agent speaks before the patient finishes a thought or answer.
- Agent asks for information the patient already provided in the immediately prior turn.
- Agent utterances appear cut off or fragmented (missing sentence beginnings).
- Tight timestamp gaps or overlap signals suggest the agent did not wait for the patient.
- Repeated verification questions caused by the agent talking over or not hearing the patient.
- Use the automated overlap signals section when present, and cross-check against transcript quotes.
- Title overlap bugs clearly, e.g. "Agent spoke over patient" or "Agent interrupted patient verification".
- For overlap bugs, set criterion to "Turn-taking: agent should wait for patient to finish" when no \
scenario criterion fits.

Return ONLY valid JSON:
{
  "summary": "One paragraph overview of the call quality",
  "bugs": [
    {
      "title": "Short bug title",
      "severity": "High",
      "quote": "Exact quote or [turn N] reference from transcript",
      "details": "What happened vs what should have happened",
      "criterion": "Which success criterion this violates, if any"
    }
  ],
  "criteria_met": ["criterion text that was satisfied"],
  "criteria_failed": ["criterion text that was NOT satisfied"]
}
"""


def evaluate_call(
    settings: Settings,
    *,
    scenario: Scenario,
    transcript_text: str,
    call_id: str,
    turns: list[dict[str, Any]] | None = None,
    events_path: Path | None = None,
) -> EvaluationResult:
    """Run GPT evaluator on transcript vs scenario success criteria."""
    client = get_openai_client()

    criteria = "\n".join(f"- {item}" for item in scenario.success_criteria)
    overlap_context = build_overlap_context(turns or [], events_path)
    user_prompt = f"""Call ID: {call_id}
Scenario: {scenario.name} ({scenario.category.value})
Description: {scenario.description}
Patient goal: {scenario.goal}

Success criteria to check:
{criteria}

{overlap_context}

Transcript:
{transcript_text}
"""

    logger.info("Evaluating call %s with model=%s", call_id, settings.openai_eval_model)
    response = client.chat.completions.create(
        model=settings.openai_eval_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    bugs = [BugFinding.model_validate(item) for item in data.get("bugs", [])]
    return EvaluationResult(
        call_id=call_id,
        summary=data.get("summary", ""),
        bugs=bugs,
        criteria_met=data.get("criteria_met", []),
        criteria_failed=data.get("criteria_failed", []),
    )
