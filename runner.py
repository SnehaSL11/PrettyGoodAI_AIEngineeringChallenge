"""CLI entry point for batch runs and single calls."""

from __future__ import annotations

import logging
import sys

import click

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@click.group()
def cli() -> None:
    """Patient voice bot — call Pretty Good AI test line with generated scenarios."""


@cli.command()
def status() -> None:
    """Show project status and config (no API calls)."""
    from config import get_settings

    settings = get_settings()
    click.echo("Patient Voice Bot")
    click.echo(f"  Target:  {settings.target_phone_number}")
    click.echo(f"  Caller:  {settings.twilio_phone_number}")
    click.echo(f"  Output:  {settings.output_dir}")
    click.echo(f"  Public:  {settings.public_base_url}")
    click.echo(f"  Planning model: {settings.openai_planning_model}")
    click.echo("")
    click.echo("Phase 6 ready — batch: python runner.py batch --count 12")
    click.echo("Start server: python main.py")
    click.echo("Call: python runner.py call --scenario outputs/call01/call01-scenario.json --analyze")


@cli.command()
@click.option("--count", default=3, show_default=True, help="Number of scenarios to generate")
def generate(count: int) -> None:
    """Generate patient test scenarios via LLM (no phone calls).

    Flow per scenario:
      1. Orchestrator picks the next test category
      2. Generator writes patient persona, goal, and success criteria
      3. Validator checks the JSON schema
      4. Scenario saved to outputs/callNN/callNN-scenario.json
      5. Entry appended to outputs/call_history.json
    """
    from config import get_settings
    from planning.planner import generate_scenarios
    from planning.validator import ScenarioValidationError

    if count < 1:
        raise click.ClickException("--count must be at least 1")

    settings = get_settings()
    click.echo(f"Generating {count} scenario(s) using {settings.openai_planning_model}...")
    click.echo("")

    try:
        results = generate_scenarios(settings, count=count)
    except ScenarioValidationError as exc:
        click.echo(f"Error: {exc}", err=True)
        if exc.errors:
            for err in exc.errors:
                click.echo(f"  - {err}", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    for result in results:
        scenario = result.scenario
        click.echo(f"✓ {scenario.id}: {scenario.name}")
        click.echo(f"    category:  {scenario.category.value}")
        click.echo(f"    goal:      {scenario.goal[:80]}{'...' if len(scenario.goal) > 80 else ''}")
        click.echo(f"    saved:     {result.scenario_path}")
        click.echo(f"    rationale: {result.plan_rationale}")
        click.echo("")

    click.echo(f"Done. {len(results)} scenario(s) in {settings.output_dir}")


@cli.command()
@click.argument("seed_path", type=click.Path(exists=True, path_type=str))
def load_seed(seed_path: str) -> None:
    """Load a YAML seed scenario into outputs/callNN/ (debug helper)."""
    from pathlib import Path

    from config import get_settings
    from patient.models import CallHistoryEntry, CallStatus, load_seed_scenario, next_call_id, utc_now
    from planning.history import load_call_history, save_call_history

    settings = get_settings()
    seed = load_seed_scenario(Path(seed_path))
    call_id = next_call_id(settings.output_dir)
    seed.id = call_id
    seed.generated_at = utc_now()

    settings.ensure_call_dir(call_id)
    out_path = settings.call_scenario_path(call_id)
    seed.save(out_path)

    history = load_call_history(settings.call_history_path)
    history.add(
        CallHistoryEntry(
            call_id=call_id,
            scenario_id=seed.id,
            category=seed.category,
            status=CallStatus.GENERATED,
            scenario_path=str(out_path),
            created_at=utc_now(),
            notes=f"Loaded from seed: {seed_path}",
        )
    )
    save_call_history(settings.call_history_path, history)

    click.echo(f"✓ Loaded seed as {call_id}")
    click.echo(f"  saved: {out_path}")


@cli.command("call")
@click.option(
    "--scenario",
    "scenario_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to scenario JSON (e.g. outputs/call01/call01-scenario.json)",
)
@click.option(
    "--bridge-mode",
    type=click.Choice(["realtime", "silent", "echo"], case_sensitive=False),
    default="realtime",
    show_default=True,
    help="realtime=OpenAI patient voice, silent/echo=Phase 3 debug modes",
)
@click.option(
    "--analyze/--no-analyze",
    default=False,
    help="Run post-call transcription + bug evaluation after the call",
)
def call(scenario_path: str, bridge_mode: str, analyze: bool) -> None:
    """Place one outbound Twilio call with an AI patient (OpenAI Realtime).

    Prerequisites:
      1. FastAPI running:  python main.py
      2. ngrok tunnel:     ngrok http 8000
      3. PUBLIC_BASE_URL in .env matches ngrok https URL (restart server after change)
    """
    from pathlib import Path

    from config import get_settings
    from telephony.call_service import place_call_and_wait
    from telephony.twilio_client import TelephonyError

    settings = get_settings()
    click.echo(f"Placing call for scenario: {scenario_path}")
    click.echo(f"  Target:      {settings.target_phone_number}")
    click.echo(f"  From:        {settings.twilio_phone_number}")
    click.echo(f"  Webhooks:    {settings.public_base_url}")
    click.echo(f"  Bridge mode: {bridge_mode}")
    click.echo("")
    click.echo("Ensure python main.py is running and ngrok is pointed at port 8000.")
    click.echo("")

    try:
        result = place_call_and_wait(
            settings,
            scenario_path=Path(scenario_path),
            bridge_mode=bridge_mode,
        )
    except TelephonyError as exc:
        click.echo(f"Telephony error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if result["success"]:
        click.echo(f"✓ Call completed: {result['call_id']}")
    else:
        click.echo(f"✗ Call ended with status: {result['twilio_status']}", err=True)

    click.echo(f"  Twilio SID:  {result['twilio_call_sid']}")
    click.echo(f"  Session log: {result['session_log']}")
    if result["recording_path"]:
        click.echo(f"  Recording:   {result['recording_path']}")
    else:
        click.echo("  Recording:   not ready yet (check server logs / outputs/callNN/)")

    if not result["success"]:
        sys.exit(1)

    if analyze:
        if not result["recording_path"]:
            click.echo("Skipping analysis — recording not available yet.", err=True)
            sys.exit(1)
        _run_analysis(result["call_id"])


@cli.command()
@click.option(
    "--count",
    default=12,
    show_default=True,
    help="Number of scenarios to generate, call, and analyze",
)
@click.option(
    "--bridge-mode",
    type=click.Choice(["realtime", "silent", "echo"], case_sensitive=False),
    default="realtime",
    show_default=True,
    help="realtime=OpenAI patient voice, silent/echo=Phase 3 debug modes",
)
@click.option(
    "--continue-on-error/--no-continue-on-error",
    default=True,
    show_default=True,
    help="Continue remaining calls if one step fails",
)
def batch(count: int, bridge_mode: str, continue_on_error: bool) -> None:
    """Full pipeline: generate scenarios → place calls → post-call analysis.

    Prerequisites (same as ``call``):
      1. FastAPI running:  python main.py
      2. ngrok tunnel:     ngrok http 8000
      3. PUBLIC_BASE_URL in .env matches ngrok https URL (restart server after change)
    """
    exit_code = _run_batch(
        count=count,
        bridge_mode=bridge_mode,
        continue_on_error=continue_on_error,
    )
    if exit_code != 0:
        sys.exit(exit_code)


def _run_batch(
    *,
    count: int,
    bridge_mode: str,
    continue_on_error: bool,
) -> int:
    from pathlib import Path

    from analysis.pipeline import analyze_call
    from config import get_settings
    from planning.planner import generate_scenarios
    from planning.validator import ScenarioValidationError

    if count < 1:
        raise click.ClickException("--count must be at least 1")

    settings = get_settings()
    click.echo(f"Batch run: {count} call(s)")
    click.echo(f"  Target:      {settings.target_phone_number}")
    click.echo(f"  From:        {settings.twilio_phone_number}")
    click.echo(f"  Webhooks:    {settings.public_base_url}")
    click.echo(f"  Bridge mode: {bridge_mode}")
    click.echo("")
    click.echo("Ensure python main.py is running and ngrok is pointed at port 8000.")
    click.echo("")

    try:
        generated = generate_scenarios(settings, count=count)
    except ScenarioValidationError as exc:
        click.echo(f"Scenario generation failed: {exc}", err=True)
        return 1
    except Exception as exc:
        click.echo(f"Scenario generation failed: {exc}", err=True)
        return 1

    click.echo(f"Generated {len(generated)} scenario(s).")
    click.echo("")

    summaries: list[dict[str, object]] = []
    had_failure = False

    for index, item in enumerate(generated, start=1):
        scenario = item.scenario
        scenario_path = Path(item.scenario_path)
        click.echo(f"=== [{index}/{len(generated)}] {scenario.id}: {scenario.name} ===")

        call_result = _place_call_with_retry(
            settings,
            scenario_path=scenario_path,
            bridge_mode=bridge_mode,
        )
        if call_result is None:
            had_failure = True
            summaries.append(
                {
                    "call_id": scenario.id,
                    "call_ok": False,
                    "analyze_ok": False,
                    "bugs": 0,
                }
            )
            if not continue_on_error:
                break
            click.echo("")
            continue

        call_ok = bool(call_result["success"])
        if call_ok:
            click.echo(f"✓ Call completed: {call_result['call_id']}")
        else:
            click.echo(
                f"✗ Call ended with status: {call_result['twilio_status']}",
                err=True,
            )
            had_failure = True

        click.echo(f"  Twilio SID:  {call_result['twilio_call_sid']}")
        click.echo(f"  Session log: {call_result['session_log']}")
        if call_result["recording_path"]:
            click.echo(f"  Recording:   {call_result['recording_path']}")
        else:
            click.echo("  Recording:   not ready yet (check server logs / outputs/callNN/)")

        analyze_ok = False
        bug_count = 0
        if call_result["recording_path"]:
            click.echo(f"\nAnalyzing {call_result['call_id']}...")
            try:
                analysis = analyze_call(settings, call_result["call_id"])
                analyze_ok = True
                bug_count = analysis.bug_count
                click.echo(f"✓ Transcript:  {analysis.transcript_txt_path}")
                click.echo(f"✓ Full JSON:   {analysis.transcript_json_path}")
                click.echo(f"✓ Bugs found:  {analysis.bug_count}")
                click.echo(f"  Summary:     {analysis.evaluation_summary[:120]}...")
            except Exception as exc:
                had_failure = True
                click.echo(f"Analysis error for {call_result['call_id']}: {exc}", err=True)
                if not continue_on_error:
                    break
        else:
            had_failure = True
            click.echo(
                f"Skipping analysis for {call_result['call_id']} — recording not available.",
                err=True,
            )
            if not continue_on_error:
                break

        summaries.append(
            {
                "call_id": call_result["call_id"],
                "call_ok": call_ok,
                "analyze_ok": analyze_ok,
                "bugs": bug_count,
            }
        )
        click.echo("")

    click.echo("=== Batch summary ===")
    for row in summaries:
        call_id = row["call_id"]
        call_ok = "ok" if row["call_ok"] else "FAILED"
        if row["analyze_ok"]:
            analysis_label = f"ok ({row['bugs']} bug(s))"
        elif row["call_ok"]:
            analysis_label = "skipped"
        else:
            analysis_label = "n/a"
        click.echo(f"  {call_id}: call={call_ok}, analyze={analysis_label}")

    click.echo(f"\nBug report: {settings.bug_report_path}")
    return 1 if had_failure else 0


def _place_call_with_retry(
    settings,
    *,
    scenario_path,
    bridge_mode: str,
):
    from telephony.call_service import place_call_and_wait
    from telephony.twilio_client import TelephonyError

    for attempt in range(2):
        try:
            return place_call_and_wait(
                settings,
                scenario_path=scenario_path,
                bridge_mode=bridge_mode,
            )
        except TelephonyError as exc:
            if attempt == 0:
                click.echo(f"Telephony error (retrying once): {exc}", err=True)
                continue
            click.echo(f"Telephony error: {exc}", err=True)
            return None
        except Exception as exc:
            click.echo(f"Call error: {exc}", err=True)
            return None
    return None


@cli.command()
@click.option(
    "--call-id",
    default=None,
    help="Analyze one call, e.g. call-01",
)
@click.option(
    "--all",
    "analyze_all",
    is_flag=True,
    help="Analyze every recording under outputs/callNN/",
)
def analyze(call_id: str | None, analyze_all: bool) -> None:
    """Post-call analysis: Whisper transcript + bug evaluation.

    Produces per call under outputs/callNN/:
      callNN-transcript.txt
      callNN-transcript-full.json
      callNN-bugs.md
    Appends to outputs/bug_report.md
    """
    from config import get_settings
    from analysis.pipeline import analyze_all_recordings, analyze_call

    settings = get_settings()

    if analyze_all:
        click.echo("Analyzing all recordings...")
        results = analyze_all_recordings(settings)
        for item in results:
            click.echo(f"✓ {item.call_id}: {item.bug_count} bug(s)")
            click.echo(f"    transcript: {item.transcript_txt_path}")
        click.echo(f"\nBug report: {settings.bug_report_path}")
        return

    if not call_id:
        raise click.ClickException("Provide --call-id call-01 or --all")

    _run_analysis(call_id)


def _run_analysis(call_id: str) -> None:
    from config import get_settings
    from analysis.pipeline import analyze_call

    settings = get_settings()
    click.echo(f"\nAnalyzing {call_id}...")
    try:
        result = analyze_call(settings, call_id)
    except Exception as exc:
        click.echo(f"Analysis error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"✓ Transcript:  {result.transcript_txt_path}")
    click.echo(f"✓ Full JSON:   {result.transcript_json_path}")
    click.echo(f"✓ Bugs found:  {result.bug_count}")
    click.echo(f"  Summary:     {result.evaluation_summary[:120]}...")
    click.echo(f"✓ Bug report:  {settings.bug_report_path}")


if __name__ == "__main__":
    cli()
