"""testspec CLI — Spec-driven test case generation toolkit.

Usage:
    testspec init                              Initialize .testspec/ in current project
    testspec analyze <prd> -o <name>           Analyze PRD → functional modules
    testspec list [-o <name>]                  List all modules with progress
    testspec strategy [-o <name>] [--module]   Generate test strategy
    testspec generate [-o <name>] [--module]   Generate test cases
    testspec review [-o <name>] [--module]     Review coverage & quality
    testspec export [-o <name>]                Export cases to Excel
    testspec status [-o <name>]                Show workflow progress
    testspec run <prd> -o <name>               Run the full pipeline end-to-end
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from testspec.core import workflow
from testspec.core.exporter import export_excel
from testspec import __version__

app = typer.Typer(
    name="testspec",
    help="[√] testspec — Spec-driven test case generation from PRD to Excel.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool):
    if value:
        console.print(f"[√] testspec version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, help="Show version and exit."),
):
    """testspec — Spec-driven test case generation from PRD to Excel."""
    pass
console = Console()


def _project_dir() -> Path:
    return Path.cwd()


# ── init ───────────────────────────────────────────────

@app.command()
def init():
    """Initialize .testspec/ directory in the current project."""
    workflow.init(_project_dir())


# ── analyze ────────────────────────────────────────────

@app.command()
def analyze(
    prd: str = typer.Argument(..., help="Path to the PRD markdown file"),
    output: str = typer.Option(..., "-o", "--output", help="Output feature name (creates tests/<name>/ directory)"),
    mode: str = typer.Option("api", "-m", "--mode", help="Execution mode: api or prompt"),
):
    """Stage 1: Analyze PRD and decompose into testable modules."""
    console.print(Panel(f"[bold]Stage 1: ANALYZE[/bold] — 分析 PRD 文档", border_style="blue"))
    workflow.analyze(_project_dir(), prd, output, mode)


# ── list ───────────────────────────────────────────────

@app.command()
def list(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
):
    """List all modules from analysis with progress status."""
    console.print(Panel(f"[bold]Module List[/bold] — 模块清单", border_style="blue"))
    workflow.list_modules(_project_dir(), output)


# ── strategy ───────────────────────────────────────────

@app.command()
def strategy(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
    module: Optional[str] = typer.Option(None, "--module", help="Specific module ID to process (e.g., '002-coupon-claim')"),
    all_modules: bool = typer.Option(False, "--all-modules", help="Process all modules"),
    mode: str = typer.Option("api", "-m", "--mode", help="Execution mode: api or prompt"),
):
    """Stage 2: Generate test strategy based on analysis."""
    console.print(Panel(f"[bold]Stage 2: STRATEGY[/bold] — 制定测试策略", border_style="blue"))
    workflow.strategy(_project_dir(), output, module, all_modules, mode)


# ── generate ───────────────────────────────────────────

@app.command()
def generate(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
    module: Optional[str] = typer.Option(None, "--module", help="Specific module ID to generate cases for (e.g., '002-coupon-claim')"),
    all_modules: bool = typer.Option(False, "--all-modules", help="Generate cases for all modules"),
    mode: str = typer.Option("api", "-m", "--mode", help="Execution mode: api or prompt"),
):
    """Stage 3: Generate structured test cases."""
    console.print(Panel(f"[bold]Stage 3: GENERATE[/bold] — 生成测试用例", border_style="blue"))
    workflow.generate(_project_dir(), output, module, all_modules, mode)


# ── review ─────────────────────────────────────────────

@app.command()
def review(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
    module: Optional[str] = typer.Option(None, "--module", help="Specific module ID to review (e.g., '002-coupon-claim')"),
    all_modules: bool = typer.Option(False, "--all-modules", help="Review all modules"),
    mode: str = typer.Option("api", "-m", "--mode", help="Execution mode: api or prompt"),
):
    """Stage 4: Review coverage and identify gaps."""
    console.print(Panel(f"[bold]Stage 4: REVIEW[/bold] — 覆盖率审查", border_style="blue"))
    workflow.review(_project_dir(), output, module, all_modules, mode)


# ── export ─────────────────────────────────────────────

@app.command()
def export(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
    out_file: str = typer.Option("", "-f", "--file", help="Output Excel file path (default: tests/<feature>/cases.xlsx)"),
):
    """Stage 5: Export test cases to Excel."""
    console.print(Panel(f"[bold]Stage 5: EXPORT[/bold] — 导出 Excel", border_style="blue"))
    project = _project_dir()
    
    # Resolve feature name
    feature = output or workflow._get_default_feature(project)
    if not feature:
        console.print("[red]Error: No -o specified and no default_feature in config.[/red]")
        console.print("[dim]Run 'testspec analyze -o <name>' first or specify -o.[/dim]")
        raise typer.Exit(1)
    
    fd = project / "tests" / feature
    cases_path = fd / "cases.md"

    if not cases_path.exists():
        console.print(f"[red]Error: {cases_path} not found. Run 'testspec generate' first.[/red]")
        raise typer.Exit(1)

    out_path = Path(out_file) if out_file else fd / "cases.xlsx"
    export_excel(cases_path, out_path, feature_name=feature)


# ── status ─────────────────────────────────────────────

@app.command()
def status(
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Feature name (uses default from config if not specified)"),
):
    """Show workflow status for a feature."""
    workflow.status(_project_dir(), output)


# ── run (full pipeline) ───────────────────────────────

@app.command()
def run(
    prd: str = typer.Argument(..., help="Path to the PRD markdown file"),
    output: str = typer.Option(..., "-o", "--output", help="Output feature name"),
    mode: str = typer.Option("api", "-m", "--mode", help="Execution mode: api or prompt"),
    export_xlsx: bool = typer.Option(True, "--export/--no-export", help="Also export to Excel"),
):
    """Run the full pipeline: analyze → strategy → generate → review → export."""
    console.print(
        Panel(
            f"[bold]Full Pipeline[/bold] for [cyan]{output}[/cyan]\n"
            f"PRD: {prd}  |  Mode: {mode}",
            title="[√] testspec",
            border_style="green",
        )
    )

    console.print("\n[bold blue]━━━ Stage 1/4: ANALYZE ━━━[/bold blue]")
    workflow.analyze(_project_dir(), prd, output, mode)

    if mode == "prompt":
        console.print("\n[yellow]Prompt mode: prompts exported for all stages. Execute them manually in order.[/yellow]")
        _export_remaining_prompts(output, mode)
        return

    console.print("\n[bold blue]━━━ Stage 2/4: STRATEGY ━━━[/bold blue]")
    workflow.strategy(_project_dir(), output, None, True, mode)

    console.print("\n[bold blue]━━━ Stage 3/4: GENERATE ━━━[/bold blue]")
    workflow.generate(_project_dir(), output, None, True, mode)

    console.print("\n[bold blue]━━━ Stage 4/4: REVIEW ━━━[/bold blue]")
    workflow.review(_project_dir(), output, None, True, mode)

    if export_xlsx:
        console.print("\n[bold blue]━━━ EXPORT ━━━[/bold blue]")
        project = _project_dir()
        fd = project / "tests" / output
        export_excel(fd / "cases.md", fd / "cases.xlsx", feature_name=output)

    console.print(
        Panel(
            f"[bold green]Pipeline complete![/bold green]\n\n"
            f"  tests/{output}/analysis.md  — PRD 分析\n"
            f"  tests/{output}/strategy.md  — 测试策略\n"
            f"  tests/{output}/cases.md     — 测试用例\n"
            f"  tests/{output}/review.md    — 覆盖率审查\n"
            f"  tests/{output}/cases.xlsx   — Excel 导出",
            title="✅ Done",
            border_style="green",
        )
    )


def _export_remaining_prompts(feature: str, mode: str) -> None:
    """In prompt mode, export prompts for stages that need prior stage output."""
    console.print(
        "\n[dim]Tip: After executing the analyze prompt, run:[/dim]\n"
        f"  testspec strategy -o {feature} -m prompt\n"
        f"  testspec generate -o {feature} -m prompt\n"
        f"  testspec review -o {feature} -m prompt\n"
        f"  testspec export -o {feature}\n"
    )


if __name__ == "__main__":
    app()
