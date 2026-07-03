"""Read and write outputs/call_history.json."""

from __future__ import annotations

import json
from pathlib import Path

from patient.models import CallHistory


def load_call_history(path: Path) -> CallHistory:
    if not path.exists():
        return CallHistory()
    data = json.loads(path.read_text(encoding="utf-8"))
    return CallHistory.model_validate(data)


def save_call_history(path: Path, history: CallHistory) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        history.model_dump_json(indent=2),
        encoding="utf-8",
    )


def summarize_recent_entries(history: CallHistory, limit: int = 5) -> str:
    if not history.entries:
        return ""
    lines: list[str] = []
    for entry in history.entries[-limit:]:
        lines.append(
            f"- {entry.call_id}: category={entry.category.value}, "
            f"status={entry.status.value}, scenario={entry.scenario_path}"
        )
    return "\n".join(lines)
