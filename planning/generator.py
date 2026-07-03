"""Scenario generator — LLM writes a full patient test scenario."""

from __future__ import annotations

import json
import logging

from config import Settings
from patient.models import OrchestratorPlan, Scenario, utc_now
from planning.llm import get_openai_client
from planning.prompts import GENERATOR_SYSTEM_PROMPT, build_generator_user_prompt
from planning.validator import ScenarioValidationError, validate_generated_scenario

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def generate_scenario(
    settings: Settings,
    *,
    call_id: str,
    plan: OrchestratorPlan,
) -> Scenario:
    """Generate and validate a scenario from an orchestrator plan."""
    client = get_openai_client()
    user_prompt = build_generator_user_prompt(
        call_id=call_id,
        plan_category=plan.next_category.value,
        hint=plan.hint,
        avoid=plan.avoid,
    )

    last_error: ScenarioValidationError | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model=settings.openai_planning_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
        )
        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
            scenario = validate_generated_scenario(
                data,
                call_id=call_id,
                expected_category=plan.next_category,
                orchestrator_hint=plan.hint,
            )
            scenario.generated_at = utc_now()
            logger.info(
                "Generated scenario %s: %s (%s)",
                call_id,
                scenario.name,
                scenario.category.value,
            )
            return scenario
        except (json.JSONDecodeError, ScenarioValidationError) as exc:
            last_error = (
                exc
                if isinstance(exc, ScenarioValidationError)
                else ScenarioValidationError(f"Invalid JSON from generator: {exc}")
            )
            logger.warning("Generator attempt %s failed for %s: %s", attempt, call_id, last_error)
            if last_error.errors:
                user_prompt += f"\n\nValidation errors: {'; '.join(last_error.errors)}"
            user_prompt += "\nFix the issues and return only valid JSON."

    raise last_error or ScenarioValidationError(f"Generator failed for {call_id}")
