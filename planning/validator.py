"""Validate LLM-generated scenario JSON before saving or calling."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from patient.models import OrchestratorPlan, PatientProfile, Scenario, ScenarioCategory


class ScenarioValidationError(ValueError):
    """Raised when generated scenario JSON fails validation."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


def validate_orchestrator_plan(data: dict[str, Any]) -> OrchestratorPlan:
    try:
        return OrchestratorPlan.model_validate(data)
    except ValidationError as exc:
        raise ScenarioValidationError(
            "Orchestrator plan failed validation",
            errors=[err["msg"] for err in exc.errors()],
        ) from exc


def validate_generated_scenario(
    data: dict[str, Any],
    *,
    call_id: str,
    expected_category: ScenarioCategory | None = None,
    orchestrator_hint: str | None = None,
) -> Scenario:
    """Validate raw generator JSON and build a Scenario model."""
    errors: list[str] = []

    for field in ("name", "description", "goal", "behavior", "success_criteria", "patient"):
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        raise ScenarioValidationError("Scenario missing required fields", errors=errors)

    try:
        category = ScenarioCategory(data["category"])
    except (ValueError, KeyError) as exc:
        raise ScenarioValidationError(
            f"Invalid category: {data.get('category')!r}",
            errors=[f"Must be one of: {[c.value for c in ScenarioCategory]}"],
        ) from exc

    if expected_category and category != expected_category:
        raise ScenarioValidationError(
            f"Category mismatch: expected {expected_category.value}, got {category.value}"
        )

    if len(data.get("behavior", [])) < 3:
        errors.append("behavior must have at least 3 items")
    if len(data.get("success_criteria", [])) < 3:
        errors.append("success_criteria must have at least 3 items")

    try:
        patient = PatientProfile.model_validate(data["patient"])
    except ValidationError as exc:
        errors.extend(err["msg"] for err in exc.errors())

    if errors:
        raise ScenarioValidationError("Scenario validation failed", errors=errors)

    return Scenario(
        id=call_id,
        category=category,
        name=str(data["name"]).strip(),
        description=str(data["description"]).strip(),
        patient=patient,
        goal=str(data["goal"]).strip(),
        behavior=[str(item).strip() for item in data["behavior"]],
        success_criteria=[str(item).strip() for item in data["success_criteria"]],
        tags=[str(tag).strip() for tag in data.get("tags", [])],
        orchestrator_hint=orchestrator_hint,
        source="generated",
    )
