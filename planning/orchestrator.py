"""Orchestrator — LLM decides what category of test to run next."""

from __future__ import annotations

import json
import logging

from config import Settings
from patient.models import OrchestratorPlan
from planning.history import summarize_recent_entries
from planning.llm import get_openai_client
from planning.prompts import ORCHESTRATOR_SYSTEM_PROMPT, build_orchestrator_user_prompt
from planning.validator import ScenarioValidationError, validate_orchestrator_plan

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def plan_next_scenario(
    settings: Settings,
    *,
    categories_used: list[str],
    recent_entries_summary: str,
    bug_report_excerpt: str,
    scenario_index: int,
    total_scenarios: int,
) -> OrchestratorPlan:
    """Ask the planning LLM what to test next."""
    client = get_openai_client()
    user_prompt = build_orchestrator_user_prompt(
        categories_used=categories_used,
        recent_entries_summary=recent_entries_summary,
        bug_report_excerpt=bug_report_excerpt,
        scenario_index=scenario_index,
        total_scenarios=total_scenarios,
    )

    last_error: ScenarioValidationError | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model=settings.openai_planning_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
            plan = validate_orchestrator_plan(data)
            logger.info(
                "Orchestrator plan (attempt %s): category=%s hint=%s",
                attempt,
                plan.next_category.value,
                plan.hint,
            )
            return plan
        except (json.JSONDecodeError, ScenarioValidationError) as exc:
            last_error = (
                exc
                if isinstance(exc, ScenarioValidationError)
                else ScenarioValidationError(f"Invalid JSON from orchestrator: {exc}")
            )
            logger.warning("Orchestrator attempt %s failed: %s", attempt, last_error)
            user_prompt += (
                f"\n\nYour previous response was invalid ({last_error}). "
                "Return only valid JSON matching the required schema."
            )

    raise last_error or ScenarioValidationError("Orchestrator failed after retries")
