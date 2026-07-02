"""CLI entry point for batch runs and single calls.

Implemented in Phase 2+.
"""

import click


@click.group()
def cli() -> None:
    """Patient voice bot — call Pretty Good AI test line with generated scenarios."""


@cli.command()
def status() -> None:
    """Show project status and config (no API calls)."""
    from config import get_settings

    settings = get_settings()
    click.echo("Patient Voice Bot — Phase 1 foundation ready")
    click.echo(f"  Target:  {settings.target_phone_number}")
    click.echo(f"  Caller:  {settings.twilio_phone_number}")
    click.echo(f"  Output:  {settings.output_dir}")
    click.echo(f"  Public:  {settings.public_base_url}")
    click.echo("")
    click.echo("Next: Phase 2 — planning layer (orchestrator + generator)")


if __name__ == "__main__":
    cli()
