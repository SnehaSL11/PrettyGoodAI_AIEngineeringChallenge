"""Post-call analysis orchestration."""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from analysis.bug_report import append_bug_report, format_call_report_section
from analysis.evaluator import evaluate_call
from analysis.transcriber import transcribe_recording
from analysis.transcript_merger import build_full_transcript, format_readable_transcript
from config import Settings, call_id_from_slug, call_slug
from patient.models import CallStatus, Scenario, utc_now
from planning.history import load_call_history, save_call_history

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Artifacts produced by post-call analysis."""

    call_id: str
    transcript_txt_path: Path
    transcript_json_path: Path
    bug_count: int
    evaluation_summary: str


def _legacy_paths(settings: Settings, call_id: str) -> dict[str, Path]:
    return {
        "recording": settings.output_dir / "recordings" / f"{call_id}.mp3",
        "scenario": settings.output_dir / "scenarios" / f"{call_id}.json",
        "events": settings.output_dir / "logs" / f"{call_id}-events.json",
        "session": settings.output_dir / "logs" / f"{call_id}-session.json",
        "transcript_txt": settings.output_dir / "transcripts" / f"{call_id}.txt",
        "transcript_json": settings.output_dir / "transcripts" / f"{call_id}-full.json",
    }


def _read_paths(settings: Settings, call_id: str) -> dict[str, Path]:
    """Resolve artifact locations for reading (per-call folder, then legacy flat layout)."""
    paths = settings.call_paths(call_id)
    resolved = dict(paths)
    for key, legacy_path in _legacy_paths(settings, call_id).items():
        if not resolved[key].exists() and legacy_path.exists():
            resolved[key] = legacy_path
    return resolved


def materialize_call_folder(settings: Settings, call_id: str) -> dict[str, Path]:
    """Ensure all known artifacts for a call live in outputs/callNN/."""
    settings.ensure_call_dir(call_id)
    write_paths = settings.call_paths(call_id)
    read_paths = _read_paths(settings, call_id)

    for key in ("scenario", "recording", "events", "session"):
        if not write_paths[key].exists() and read_paths[key].exists():
            shutil.copy2(read_paths[key], write_paths[key])
            logger.info("Copied %s to %s", key, write_paths[key])

    canonical_scenario = write_paths["scenario"]
    if canonical_scenario.exists():
        history = load_call_history(settings.call_history_path)
        for entry in history.entries:
            if entry.call_id == call_id:
                entry.scenario_path = str(canonical_scenario)
                break
        save_call_history(settings.call_history_path, history)

    return write_paths


def _update_history_bug_count(settings: Settings, call_id: str, bug_count: int) -> None:
    history = load_call_history(settings.call_history_path)
    for entry in history.entries:
        if entry.call_id == call_id:
            entry.bug_count = bug_count
            if entry.status != CallStatus.FAILED:
                entry.status = CallStatus.COMPLETED
            entry.completed_at = entry.completed_at or utc_now()
            break
    save_call_history(settings.call_history_path, history)


def analyze_call(settings: Settings, call_id: str) -> AnalysisResult:
    """Transcribe, merge, evaluate, and write artifacts for one call."""
    paths = materialize_call_folder(settings, call_id)

    if not paths["recording"].exists():
        raise FileNotFoundError(f"Recording missing for {call_id}: {paths['recording']}")
    if not paths["scenario"].exists():
        raise FileNotFoundError(f"Scenario missing for {call_id}: {paths['scenario']}")

    scenario = Scenario.load(paths["scenario"])

    whisper_text = transcribe_recording(settings, paths["recording"])
    full_transcript = build_full_transcript(
        call_id=call_id,
        scenario_path=str(paths["scenario"]),
        recording_path=str(paths["recording"]),
        whisper_text=whisper_text,
        events_path=paths["events"],
        session_log_path=paths["session"],
    )

    readable = format_readable_transcript(full_transcript)
    paths["transcript_txt"].write_text(readable, encoding="utf-8")
    paths["transcript_json"].write_text(
        json.dumps(full_transcript, indent=2),
        encoding="utf-8",
    )

    evaluation = evaluate_call(
        settings,
        scenario=scenario,
        transcript_text=readable,
        call_id=call_id,
        turns=full_transcript.get("turns", []),
        events_path=paths["events"],
    )

    slug = call_slug(call_id)
    section = format_call_report_section(
        evaluation=evaluation,
        scenario=scenario,
        transcript_filename=f"{slug}-transcript.txt",
        recording_filename=f"{slug}-recording.mp3",
        scenario_filename=f"{slug}-scenario.json",
    )
    append_bug_report(settings.bug_report_path, section, call_id=call_id)
    paths["bugs"].write_text(section, encoding="utf-8")

    _update_history_bug_count(settings, call_id, len(evaluation.bugs))

    logger.info(
        "Analysis complete for %s: %s bugs, transcript=%s",
        call_id,
        len(evaluation.bugs),
        paths["transcript_txt"],
    )

    return AnalysisResult(
        call_id=call_id,
        transcript_txt_path=paths["transcript_txt"],
        transcript_json_path=paths["transcript_json"],
        bug_count=len(evaluation.bugs),
        evaluation_summary=evaluation.summary,
    )


def analyze_all_recordings(settings: Settings) -> list[AnalysisResult]:
    """Analyze every call that has a recording MP3."""
    results: list[AnalysisResult] = []
    seen: set[str] = set()

    for recording in sorted(settings.output_dir.glob("call[0-9][0-9]/call[0-9][0-9]-recording.mp3")):
        call_id = call_id_from_slug(recording.parent.name)
        seen.add(call_id)
        try:
            results.append(analyze_call(settings, call_id))
        except Exception as exc:
            logger.exception("Failed to analyze %s: %s", call_id, exc)

    legacy_recordings = settings.output_dir / "recordings"
    if legacy_recordings.is_dir():
        for recording in sorted(legacy_recordings.glob("call-*.mp3")):
            call_id = recording.stem
            if call_id in seen:
                continue
            try:
                results.append(analyze_call(settings, call_id))
            except Exception as exc:
                logger.exception("Failed to analyze %s: %s", call_id, exc)

    return results
