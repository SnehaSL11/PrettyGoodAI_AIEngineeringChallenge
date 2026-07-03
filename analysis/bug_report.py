"""Append structured findings to outputs/bug_report.md."""

from __future__ import annotations

from pathlib import Path

from analysis.models import EvaluationResult
from patient.models import Scenario


def _severity_emoji(severity: str) -> str:
    normalized = severity.strip().lower()
    if normalized == "high":
        return "HIGH"
    if normalized == "medium":
        return "MEDIUM"
    return "LOW"


def format_call_report_section(
    *,
    evaluation: EvaluationResult,
    scenario: Scenario,
    transcript_filename: str,
    recording_filename: str,
    scenario_filename: str | None = None,
) -> str:
    """Format one call's evaluation as markdown."""
    scenario_ref = scenario_filename or f"{scenario.id}.json"
    lines: list[str] = [
        f"## {evaluation.call_id}: {scenario.name}",
        "",
        f"**Category:** {scenario.category.value}  ",
        f"**Recording:** `{recording_filename}`  ",
        f"**Transcript:** `{transcript_filename}`  ",
        f"**Scenario:** `{scenario_ref}`",
        "",
        f"**Summary:** {evaluation.summary}",
        "",
    ]

    if evaluation.bugs:
        lines.append("### Bugs found")
        lines.append("")
        for bug in evaluation.bugs:
            lines.extend(
                [
                    f"### Bug: {bug.title}",
                    f"**Severity:** {_severity_emoji(bug.severity)}",
                    f"**Call:** {transcript_filename} — {bug.quote}",
                    f"**Details:** {bug.details}",
                ]
            )
            if bug.criterion:
                lines.append(f"**Criterion:** {bug.criterion}")
            lines.append("")
    else:
        lines.append("### Bugs found")
        lines.append("")
        lines.append("No significant issues detected against success criteria.")
        lines.append("")

    if evaluation.criteria_failed:
        lines.append("**Criteria failed:**")
        for item in evaluation.criteria_failed:
            lines.append(f"- {item}")
        lines.append("")

    if evaluation.criteria_met:
        lines.append("**Criteria met:**")
        for item in evaluation.criteria_met:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def append_bug_report(
    bug_report_path: Path,
    section: str,
    *,
    call_id: str,
) -> None:
    """Append a call section to bug_report.md, replacing prior section for same call_id."""
    bug_report_path.parent.mkdir(parents=True, exist_ok=True)

    header = f"## {call_id}:"
    existing = bug_report_path.read_text(encoding="utf-8") if bug_report_path.exists() else ""

    if header in existing:
        parts = existing.split("\n## ")
        kept: list[str] = []
        for part in parts:
            if not part.strip():
                continue
            block = part if part.startswith("## ") else f"## {part}"
            if not block.startswith(header):
                kept.append(block.rstrip())
        body = "\n\n".join(kept).strip()
        if body:
            body += "\n\n"
        body += section.strip()
        bug_report_path.write_text(body + "\n", encoding="utf-8")
        return

    if not existing.strip():
        existing = "# Bug Report\n\nAutomated findings from patient voice bot test calls.\n\n---\n\n"

    bug_report_path.write_text(existing.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")
