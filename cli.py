from __future__ import annotations

from pathlib import Path

import click

from .orchestrator import Orchestrator
from .report.terminal import print_terminal_report


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Project Validator — AI-powered codebase review agent."""
    pass


@cli.command()
@click.argument("project_path", type=click.Path(exists=True), default=".")
@click.option("--requirements", "-r", type=click.Path(exists=True), help="Path to requirements document")
@click.option("--output", "-o", type=click.Path(), help="Custom output directory for report")
@click.option("--model", default="claude-sonnet-5-5", help="Claude model to use")
@click.option("--skip", multiple=True, help="Skip a dimension (structure, requirements, quality, architecture, completeness)")
@click.option("--verbose", "-v", is_flag=True, help="Show agent summaries during validation")
def validate(project_path, requirements, output, model, skip, verbose):
    """Validate a project against requirements and best practices."""
    orchestrator = Orchestrator(
        model=model,
        skip_dimensions=set(skip),
    )

    report = orchestrator.run(
        project_path=Path(project_path),
        requirements_path=Path(requirements) if requirements else None,
        output_dir=Path(output) if output else None,
        verbose=verbose,
    )

    print_terminal_report(report)
