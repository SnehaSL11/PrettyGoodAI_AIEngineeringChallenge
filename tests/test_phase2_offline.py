"""Offline Phase 2 tests — no OpenAI API calls required."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Project root on sys.path when run as: python tests/test_phase2_offline.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from patient.models import (  # noqa: E402
    CallHistory,
    CallHistoryEntry,
    CallStatus,
    ScenarioCategory,
    load_seed_scenario,
    next_call_id,
    utc_now,
)
from planning.history import load_call_history, save_call_history, summarize_recent_entries  # noqa: E402
from planning.validator import (  # noqa: E402
    ScenarioValidationError,
    validate_generated_scenario,
    validate_orchestrator_plan,
)


def test_next_call_id() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        assert next_call_id(directory) == "call-01"
        call01 = directory / "call01"
        call01.mkdir()
        (call01 / "call01-scenario.json").write_text("{}")
        assert next_call_id(directory) == "call-02"
        call05 = directory / "call05"
        call05.mkdir()
        (call05 / "call05-scenario.json").write_text("{}")
        assert next_call_id(directory) == "call-06"
    print("✓ next_call_id")


def test_load_seed_scenario() -> None:
    seed_path = ROOT / "scenarios" / "seeds" / "weekend_appointment.yaml"
    scenario = load_seed_scenario(seed_path)
    assert scenario.id == "weekend_appointment"
    assert scenario.category == ScenarioCategory.EDGE_CASE
    assert scenario.patient.name == "Maya Patel"
    assert len(scenario.success_criteria) >= 3
    assert "success_criteria" not in scenario.to_patient_prompt_context()
    print("✓ load_seed_scenario")


def test_validate_orchestrator_plan() -> None:
    plan = validate_orchestrator_plan(
        {
            "next_category": "refill",
            "hint": "Patient needs blood pressure medication refill",
            "avoid": ["scheduling"],
            "rationale": "No refill scenario yet",
        }
    )
    assert plan.next_category == ScenarioCategory.REFILL
    print("✓ validate_orchestrator_plan")


def test_validate_generated_scenario() -> None:
    scenario = validate_generated_scenario(
        {
            "category": "edge_case",
            "name": "Sunday booking",
            "description": "Tests weekend scheduling",
            "patient": {
                "name": "Test User",
                "dob": "01/01/1990",
                "phone": "555-555-0100",
                "insurance": "Test Insurance",
            },
            "goal": "Try to book Sunday at 10am.",
            "behavior": ["Be polite", "Ask for Sunday", "Accept weekday if refused"],
            "success_criteria": [
                "No weekend booking",
                "Office hours mentioned",
                "Weekday offered",
            ],
            "tags": ["edge_case"],
        },
        call_id="call-99",
        expected_category=ScenarioCategory.EDGE_CASE,
    )
    assert scenario.id == "call-99"
    assert scenario.category == ScenarioCategory.EDGE_CASE
    print("✓ validate_generated_scenario")


def test_validator_rejects_bad_category() -> None:
    try:
        validate_generated_scenario(
            {
                "category": "not_a_real_category",
                "name": "Bad",
                "description": "Bad",
                "patient": {
                    "name": "X",
                    "dob": "01/01/1990",
                    "phone": "555",
                    "insurance": "Y",
                },
                "goal": "g",
                "behavior": ["a", "b", "c"],
                "success_criteria": ["1", "2", "3"],
            },
            call_id="call-bad",
        )
        raise AssertionError("expected ScenarioValidationError")
    except ScenarioValidationError:
        pass
    print("✓ validator rejects bad category")


def test_call_history_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "call_history.json"
        history = CallHistory(
            entries=[
                CallHistoryEntry(
                    call_id="call-01",
                    scenario_id="call-01",
                    category=ScenarioCategory.SCHEDULING,
                    status=CallStatus.GENERATED,
                    scenario_path="outputs/scenarios/call-01.json",
                    created_at=utc_now(),
                )
            ]
        )
        save_call_history(path, history)
        loaded = load_call_history(path)
        assert len(loaded.entries) == 1
        assert loaded.categories_used() == ["scheduling"]
        summary = summarize_recent_entries(loaded)
        assert "call-01" in summary
    print("✓ call_history roundtrip")


def test_scenario_save_load() -> None:
    from patient.models import PatientProfile, Scenario

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "scenario.json"
        scenario = Scenario(
            id="call-01",
            category=ScenarioCategory.REFILL,
            name="Refill test",
            description="desc",
            patient=PatientProfile(
                name="A",
                dob="01/01/1990",
                phone="555-0100",
                insurance="X",
            ),
            goal="Refill meds",
            behavior=["a", "b", "c"],
            success_criteria=["1", "2", "3"],
        )
        scenario.save(path)
        loaded = Scenario.load(path)
        assert loaded.id == "call-01"
        data = json.loads(path.read_text())
        assert data["category"] == "refill"
    print("✓ scenario save/load")


def main() -> None:
    print("Phase 2 offline tests\n")
    test_next_call_id()
    test_load_seed_scenario()
    test_validate_orchestrator_plan()
    test_validate_generated_scenario()
    test_validator_rejects_bad_category()
    test_call_history_roundtrip()
    test_scenario_save_load()
    print("\nAll offline tests passed.")


if __name__ == "__main__":
    main()
