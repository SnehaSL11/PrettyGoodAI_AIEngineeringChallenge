"""Planning pipeline — orchestrator + generator + save + history."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from config import Settings
from patient.models import (
    CallHistory,
    CallHistoryEntry,
    CallStatus,
    Scenario,
    next_call_id,
    utc_now,
)
from planning.generator import generate_scenario
from planning.history import load_call_history, save_call_history, summarize_recent_entries
from planning.orchestrator import plan_next_scenario

logger = logging.getLogger(__name__)


@dataclass
class GeneratedScenarioResult:
    """Result of generating one scenario."""

    scenario: Scenario
    scenario_path: Path
    plan_rationale: str


def _read_bug_report_excerpt(path: Path, max_chars: int = 1500) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... (truncated)"


def generate_one_scenario(
    settings: Settings,
    *,
    history: CallHistory,
    scenario_index: int,
    total_scenarios: int,
) -> GeneratedScenarioResult:
    """Run orchestrator → generator → save for a single scenario."""
    call_id = next_call_id(settings.output_dir)
    recent_summary = summarize_recent_entries(history)

    plan = plan_next_scenario(
        settings,
        categories_used=history.categories_used(),
        recent_entries_summary=recent_summary,
        bug_report_excerpt=_read_bug_report_excerpt(settings.bug_report_path),
        scenario_index=scenario_index,
        total_scenarios=total_scenarios,
    )

    scenario = generate_scenario(settings, call_id=call_id, plan=plan)
    settings.ensure_call_dir(call_id)
    scenario_path = settings.call_scenario_path(call_id)
    scenario.save(scenario_path)

    entry = CallHistoryEntry(
        call_id=call_id,
        scenario_id=scenario.id,
        category=scenario.category,
        status=CallStatus.GENERATED,
        scenario_path=str(scenario_path),
        created_at=utc_now(),
    )
    history.add(entry)
    save_call_history(settings.call_history_path, history)

    return GeneratedScenarioResult(
        scenario=scenario,
        scenario_path=scenario_path,
        plan_rationale=plan.rationale,
    )


def generate_scenarios(settings: Settings, count: int) -> list[GeneratedScenarioResult]:
    """Generate multiple diverse scenarios and persist them."""
    settings.ensure_output_dirs()
    history = load_call_history(settings.call_history_path)
    results: list[GeneratedScenarioResult] = []

    for index in range(1, count + 1):
        logger.info("Generating scenario %s/%s", index, count)
        result = generate_one_scenario(
            settings,
            history=history,
            scenario_index=index,
            total_scenarios=count,
        )
        results.append(result)

    return results
