from __future__ import annotations

from datetime import datetime
from pathlib import Path

import anthropic
from rich.console import Console

from .agents import (
    ArchitectureAgent,
    CompletenessAgent,
    QualityAgent,
    RequirementsAgent,
    StructureAgent,
)
from .collectors import CodebaseCollector
from .config import DIMENSION_WEIGHTS, MAX_TOKENS, MODEL, REPORT_OUTPUT_DIR
from .models import AgentResult, ValidationReport

console = Console()


class Orchestrator:

    def __init__(
        self,
        model: str = MODEL,
        max_tokens: int = MAX_TOKENS,
        skip_dimensions: set[str] | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.skip_dimensions = skip_dimensions or set()
        self.collector = CodebaseCollector()

    def run(
        self,
        project_path: Path,
        requirements_path: Path | None = None,
        output_dir: Path | None = None,
        verbose: bool = False,
    ) -> ValidationReport:
        console.print(f"\n[bold cyan]Validating project:[/bold cyan] {project_path.resolve()}\n")

        console.print("[dim]Collecting project files...[/dim]")
        snapshot = self.collector.collect(project_path, requirements_path)
        console.print(
            f"  Found [bold]{snapshot.total_files}[/bold] files, "
            f"[bold]{snapshot.total_lines}[/bold] lines\n"
        )

        agents = [
            StructureAgent(self.client, self.model, self.max_tokens),
            RequirementsAgent(self.client, self.model, self.max_tokens),
            QualityAgent(self.client, self.model, self.max_tokens),
            ArchitectureAgent(self.client, self.model, self.max_tokens),
            CompletenessAgent(self.client, self.model, self.max_tokens),
        ]

        results: list[AgentResult] = []
        for agent in agents:
            if agent.dimension in self.skip_dimensions:
                console.print(f"  [dim]Skipping {agent.name}...[/dim]")
                continue

            console.print(f"  [yellow]Running {agent.name}...[/yellow]", end="")
            result = agent.analyze(snapshot)
            results.append(result)

            if result.error:
                console.print(f" [red]FAILED[/red] — {result.error}")
            else:
                score_color = "green" if result.score >= 0.7 else "yellow" if result.score >= 0.5 else "red"
                console.print(f" [{score_color}]{result.score:.0%}[/{score_color}]")

            if verbose and not result.error:
                console.print(f"    [dim]{result.summary}[/dim]")

        report = self._aggregate(project_path, results)

        out = output_dir or (project_path / REPORT_OUTPUT_DIR)
        out.mkdir(parents=True, exist_ok=True)
        self._save_report(report, out)

        return report

    def _aggregate(self, project_path: Path, results: list[AgentResult]) -> ValidationReport:
        dimension_scores: dict[str, float] = {}
        all_mappings = []
        total_findings = 0
        critical = warning = error = passed = 0

        for r in results:
            dimension_scores[r.dimension] = r.score
            all_mappings.extend(r.requirement_mappings)
            for f in r.findings:
                total_findings += 1
                if f.severity == "critical":
                    critical += 1
                elif f.severity == "error":
                    error += 1
                elif f.severity == "warning":
                    warning += 1
                elif f.severity == "pass":
                    passed += 1

        weighted_sum = 0.0
        weight_sum = 0.0
        for dim, score in dimension_scores.items():
            w = DIMENSION_WEIGHTS.get(dim, 0.15)
            weighted_sum += score * w
            weight_sum += w

        overall = (weighted_sum / weight_sum * 100) if weight_sum > 0 else 0.0

        return ValidationReport(
            project_name=project_path.name,
            project_path=str(project_path.resolve()),
            timestamp=datetime.now(),
            overall_score=round(overall, 1),
            dimension_scores={k: round(v * 100, 1) for k, v in dimension_scores.items()},
            agent_results=results,
            requirement_mappings=all_mappings,
            total_findings=total_findings,
            critical_count=critical,
            error_count=error,
            warning_count=warning,
            pass_count=passed,
        )

    def _save_report(self, report: ValidationReport, output_dir: Path) -> None:
        json_path = output_dir / "report.json"
        json_path.write_text(report.model_dump_json(indent=2))

        from .report.html import generate_html_report
        html_path = output_dir / "report.html"
        html_path.write_text(generate_html_report(report))
