from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import ValidationReport

console = Console()


def print_terminal_report(report: ValidationReport) -> None:
    score = report.overall_score
    if score >= 70:
        score_color = "green"
        verdict = "GOOD"
    elif score >= 50:
        score_color = "yellow"
        verdict = "NEEDS WORK"
    else:
        score_color = "red"
        verdict = "POOR"

    console.print()
    console.print(Panel(
        f"[bold {score_color}]{score:.0f}/100[/bold {score_color}]  —  {verdict}",
        title=f"[bold]Project Validation: {report.project_name}[/bold]",
        border_style=score_color,
        padding=(1, 4),
    ))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension", style="cyan", min_width=16)
    table.add_column("Score", justify="center", min_width=8)
    table.add_column("Findings", justify="center", min_width=10)

    for result in report.agent_results:
        dim_score = report.dimension_scores.get(result.dimension, 0)
        color = "green" if dim_score >= 70 else "yellow" if dim_score >= 50 else "red"

        finding_counts = {}
        for f in result.findings:
            finding_counts[f.severity] = finding_counts.get(f.severity, 0) + 1

        findings_str = ", ".join(
            f"{count} {sev}" for sev, count in sorted(finding_counts.items())
        ) or "—"

        table.add_row(
            result.dimension.title(),
            f"[{color}]{dim_score:.0f}/100[/{color}]",
            findings_str,
        )

    console.print(table)

    critical_and_errors = []
    for result in report.agent_results:
        for f in result.findings:
            if f.severity in ("critical", "error"):
                critical_and_errors.append((result.dimension, f))

    if critical_and_errors:
        console.print("\n[bold red]Critical & Error Findings:[/bold red]")
        for dim, finding in critical_and_errors:
            icon = "[red]!!![/red]" if finding.severity == "critical" else "[yellow]!![/yellow]"
            location = f" ({finding.file_path})" if finding.file_path else ""
            console.print(f"  {icon} [{finding.severity}] {finding.title}{location}")
            if finding.recommendation:
                console.print(f"      [dim]{finding.recommendation}[/dim]")

    if report.requirement_mappings:
        console.print(f"\n[bold]Requirements Traceability:[/bold]")
        req_table = Table(show_header=True, header_style="bold")
        req_table.add_column("ID", min_width=6)
        req_table.add_column("Requirement", max_width=50)
        req_table.add_column("Status", justify="center", min_width=12)

        status_colors = {
            "implemented": "green",
            "partial": "yellow",
            "missing": "red",
            "unclear": "dim",
        }

        for m in report.requirement_mappings:
            color = status_colors.get(m.status, "white")
            req_text = m.requirement_text[:50] + ("..." if len(m.requirement_text) > 50 else "")
            req_table.add_row(
                m.requirement_id,
                req_text,
                f"[{color}]{m.status.upper()}[/{color}]",
            )

        console.print(req_table)

    console.print(
        f"\n[dim]Report saved to: {report.project_path}/.validation-report/[/dim]\n"
    )
