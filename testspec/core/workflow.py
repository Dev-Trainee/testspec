"""Core workflow engine — orchestrates the ANALYZE → STRATEGY → GENERATE → REVIEW pipeline."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from testspec.core.llm import LLMClient
from testspec.prompts.templates import (
    ANALYZE_SYSTEM,
    ANALYZE_USER,
    GENERATE_SYSTEM,
    GENERATE_USER,
    REVIEW_SYSTEM,
    REVIEW_USER,
    STRATEGY_SYSTEM,
    STRATEGY_USER,
)

console = Console()

SCAFFOLD_DIR = Path(__file__).resolve().parent.parent / "scaffold"
TESTSPEC_DIR_NAME = ".testspec"
TESTS_DIR_NAME = "tests"


# ── helpers ────────────────────────────────────────────

def _root(project_dir: Path) -> Path:
    return project_dir / TESTSPEC_DIR_NAME


def _tests(project_dir: Path) -> Path:
    return project_dir / TESTS_DIR_NAME


def _feature_dir(project_dir: Path, feature: str) -> Path:
    d = _tests(project_dir) / feature
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read(path: Path) -> str:
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    console.print(f"[green]✓[/green] Saved → {path}")


def _load_config(project_dir: Path) -> dict:
    cfg_path = _root(project_dir) / "config.yaml"
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return {}


def _build_llm(project_dir: Path) -> LLMClient:
    cfg = _load_config(project_dir).get("llm", {})
    return LLMClient(
        model=cfg.get("model", "gpt-4o"),
        base_url=cfg.get("base_url"),
        api_key_env=cfg.get("api_key_env", "OPENAI_API_KEY"),
        temperature=cfg.get("temperature", 0.3),
    )


def _constitution(project_dir: Path) -> str:
    path = _root(project_dir) / "constitution.md"
    if path.exists():
        return _read(path)
    return "(No constitution defined)"


def _memory_context(project_dir: Path) -> str:
    """Collect all files under .testspec/memory/ as context."""
    mem_dir = _root(project_dir) / "memory"
    if not mem_dir.exists():
        return ""
    parts: list[str] = []
    for f in sorted(mem_dir.glob("*.md")):
        parts.append(f"### 知识库：{f.stem}\n{f.read_text(encoding='utf-8')}")
    if not parts:
        return ""
    return "## 历史知识库（供参考）\n" + "\n\n".join(parts)


# ── commands ───────────────────────────────────────────

def init(project_dir: Path) -> None:
    """Initialize .testspec/ directory with scaffold files."""
    target = _root(project_dir)
    if target.exists():
        console.print("[yellow]⚠ .testspec/ already exists. Skipping init.[/yellow]")
        return

    target.mkdir(parents=True)
    (target / "memory").mkdir()
    _tests(project_dir).mkdir(exist_ok=True)

    # Copy scaffold files
    for src_file in SCAFFOLD_DIR.iterdir():
        dest = target / src_file.name
        if src_file.is_file():
            shutil.copy2(src_file, dest)

    # Copy AGENTS.md to project root
    agents_src = SCAFFOLD_DIR / "AGENTS.md"
    if agents_src.exists():
        shutil.copy2(agents_src, project_dir / "AGENTS.md")

    # Copy .cursor/commands/ for Cursor slash commands
    cursor_commands_src = SCAFFOLD_DIR / ".cursor" / "commands"
    if cursor_commands_src.exists():
        cursor_commands_dest = project_dir / ".cursor" / "commands"
        cursor_commands_dest.mkdir(parents=True, exist_ok=True)
        for f in cursor_commands_src.iterdir():
            if f.is_file():
                shutil.copy2(f, cursor_commands_dest / f.name)

    console.print(
        Panel(
            "[bold green]testspec initialized![/bold green]\n\n"
            f"  [cyan].testspec/constitution.md[/cyan]  — 测试宪法（请根据团队规范修改）\n"
            f"  [cyan].testspec/config.yaml[/cyan]      — 项目配置（LLM、输出格式等）\n"
            f"  [cyan].testspec/memory/[/cyan]           — 知识库目录（放入历史用例等）\n"
            f"  [cyan]AGENTS.md[/cyan]                   — AI Agent 协作指南（Qoder / 通用）\n"
            f"  [cyan].cursor/commands/[/cyan]           — Cursor 斜杠命令\n"
            f"  [cyan]tests/[/cyan]                      — 测试产物输出目录\n",
            title="[√] testspec",
            border_style="green",
        )
    )


def _save_config(project_dir: Path, config: dict) -> None:
    """Save config to .testspec/config.yaml."""
    cfg_path = _root(project_dir) / "config.yaml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)


def _get_default_feature(project_dir: Path) -> Optional[str]:
    """Get default feature from config."""
    cfg = _load_config(project_dir)
    return cfg.get("default_feature")


def analyze(project_dir: Path, prd_path: str, output: Optional[str] = None, mode: str = "api") -> None:
    """Stage 1: Analyze PRD → feature modules breakdown.
    
    Args:
        output: Feature name, will create tests/<output>/ directory
    """
    if output is None:
        console.print("[red]Error: -o/--output is required for analyze[/red]")
        raise ValueError("output is required")
    
    feature = output
    prd_content = _read(Path(prd_path))
    const = _constitution(project_dir)
    mem = _memory_context(project_dir)

    user_prompt = ANALYZE_USER.format(
        constitution=const,
        prd_content=prd_content,
        memory_context=mem,
    )

    if mode == "prompt":
        out = _feature_dir(project_dir, feature) / "analyze_prompt.md"
        _write(out, f"<!-- System Prompt -->\n{ANALYZE_SYSTEM}\n\n<!-- User Prompt -->\n{user_prompt}")
        console.print("[cyan]Prompt exported. Copy it to your AI IDE to execute.[/cyan]")
        return

    llm = _build_llm(project_dir)
    result = llm.chat(ANALYZE_SYSTEM, user_prompt)
    out = _feature_dir(project_dir, feature) / "analysis.md"
    _write(out, result)
    
    # Save default_feature to config
    cfg = _load_config(project_dir)
    cfg["default_feature"] = feature
    _save_config(project_dir, cfg)
    
    console.print(f"\n[bold]PRD analysis complete for feature: [cyan]{feature}[/cyan][/bold]")
    console.print(f"[dim]Default feature set to: {feature}[/dim]")


def strategy(project_dir: Path, output: Optional[str] = None, module: Optional[str] = None, all_modules: bool = False, mode: str = "api") -> None:
    """Stage 2: Generate test strategy based on analysis.
    
    Args:
        module: Specific module ID (e.g., "002-coupon-claim") to process
        all_modules: Process all modules
    """
    feature = _resolve_feature(project_dir, output)
    fd = _feature_dir(project_dir, feature)
    analysis_content = _read(fd / "analysis.md")
    const = _constitution(project_dir)
    mem = _memory_context(project_dir)
    
    # Build module filter instruction
    module_instruction = ""
    if module and not all_modules:
        module_instruction = f"\n\n【重要】请只针对模块 '{module}' 制定测试策略，不要处理其他模块。"
    elif all_modules:
        module_instruction = "\n\n【重要】请为 analysis.md 中识别的所有模块制定测试策略。"
    
    user_prompt = STRATEGY_USER.format(
        constitution=const,
        analysis_content=analysis_content,
        memory_context=mem,
    ) + module_instruction

    if mode == "prompt":
        suffix = f"_{module}" if module else ""
        out = fd / f"strategy{suffix}_prompt.md"
        _write(out, f"<!-- System Prompt -->\n{STRATEGY_SYSTEM}\n\n<!-- User Prompt -->\n{user_prompt}")
        console.print("[cyan]Prompt exported. Copy it to your AI IDE to execute.[/cyan]")
        return

    llm = _build_llm(project_dir)
    result = llm.chat(STRATEGY_SYSTEM, user_prompt)
    
    if module and not all_modules:
        # Append to existing strategy or create new
        strategy_path = fd / "strategy.md"
        if strategy_path.exists():
            existing = strategy_path.read_text(encoding="utf-8")
            result = existing + "\n\n---\n\n" + result
        _write(strategy_path, result)
        console.print(f"\n[bold]Test strategy generated for module: [cyan]{module}[/cyan][/bold]")
    else:
        _write(fd / "strategy.md", result)
        console.print(f"\n[bold]Test strategy generated for: [cyan]{feature}[/cyan][/bold]")


def generate(project_dir: Path, output: Optional[str] = None, module: Optional[str] = None, all_modules: bool = False, mode: str = "api") -> None:
    """Stage 3: Generate test cases based on strategy.
    
    Args:
        module: Specific module ID (e.g., "002-coupon-claim") to generate cases for
        all_modules: Generate cases for all modules
    """
    feature = _resolve_feature(project_dir, output)
    fd = _feature_dir(project_dir, feature)
    strategy_content = _read(fd / "strategy.md")
    analysis_content = _read(fd / "analysis.md")
    const = _constitution(project_dir)
    mem = _memory_context(project_dir)
    
    # Build module filter instruction
    module_instruction = ""
    if module and not all_modules:
        module_instruction = f"\n\n【重要】请只为模块 '{module}' 生成测试用例。输出格式：\n## {module}\n（该模块的用例）\n\n不要包含其他模块的用例。"
    elif all_modules:
        module_instruction = "\n\n【重要】请为 strategy.md 中涉及的所有模块生成测试用例。每个模块用 ## 001-module-name 格式作为标题分隔。"
    
    # Add instruction for numbered module format
    format_instruction = """

【用例编号格式】
模块 001-xxx 的用例编号为 TC-001-001, TC-001-002...
模块 002-xxx 的用例编号为 TC-002-001, TC-002-002...
以此类推。
"""
    
    user_prompt = GENERATE_USER.format(
        constitution=const,
        strategy_content=strategy_content,
        analysis_content=analysis_content,
        memory_context=mem,
    ) + module_instruction + format_instruction

    if mode == "prompt":
        suffix = f"_{module}" if module else ""
        out = fd / f"generate{suffix}_prompt.md"
        _write(out, f"<!-- System Prompt -->\n{GENERATE_SYSTEM}\n\n<!-- User Prompt -->\n{user_prompt}")
        console.print("[cyan]Prompt exported. Copy it to your AI IDE to execute.[/cyan]")
        return

    llm = _build_llm(project_dir)
    result = llm.chat(GENERATE_SYSTEM, user_prompt)
    
    cases_path = fd / "cases.md"
    if module and not all_modules:
        # Append or update specific module section
        if cases_path.exists():
            existing = cases_path.read_text(encoding="utf-8")
            # Try to replace existing module section or append
            module_header = f"## {module}"
            if module_header in existing:
                # Replace existing section
                import re
                pattern = f"## {re.escape(module)}.*?\n(?=## |\Z)"
                existing = re.sub(pattern, result + "\n\n", existing, flags=re.DOTALL)
                result = existing
            else:
                result = existing + "\n\n" + result
        _write(cases_path, result)
        console.print(f"\n[bold]Test cases generated for module: [cyan]{module}[/cyan][/bold]")
    else:
        _write(cases_path, result)
        console.print(f"\n[bold]Test cases generated for: [cyan]{feature}[/cyan][/bold]")


def review(project_dir: Path, output: Optional[str] = None, module: Optional[str] = None, all_modules: bool = False, mode: str = "api") -> None:
    """Stage 4: Review coverage and quality.
    
    Args:
        module: Specific module ID (e.g., "002-coupon-claim") to review
        all_modules: Review all modules
    """
    feature = _resolve_feature(project_dir, output)
    fd = _feature_dir(project_dir, feature)
    cases_content = _read(fd / "cases.md")
    analysis_content = _read(fd / "analysis.md")
    strategy_content = _read(fd / "strategy.md")
    const = _constitution(project_dir)
    
    # Build module filter instruction
    module_instruction = ""
    if module and not all_modules:
        module_instruction = f"\n\n【重要】请只审查模块 '{module}' 的测试用例覆盖率，从 cases.md 中提取该模块的用例进行分析。"
    elif all_modules:
        module_instruction = "\n\n【重要】请审查所有模块的测试用例覆盖率，按模块分别给出审查结果。"

    user_prompt = REVIEW_USER.format(
        constitution=const,
        analysis_content=analysis_content,
        strategy_content=strategy_content,
        cases_content=cases_content,
    ) + module_instruction

    if mode == "prompt":
        suffix = f"_{module}" if module else ""
        out = fd / f"review{suffix}_prompt.md"
        _write(out, f"<!-- System Prompt -->\n{REVIEW_SYSTEM}\n\n<!-- User Prompt -->\n{user_prompt}")
        console.print("[cyan]Prompt exported. Copy it to your AI IDE to execute.[/cyan]")
        return

    llm = _build_llm(project_dir)
    result = llm.chat(REVIEW_SYSTEM, user_prompt)
    
    review_path = fd / "review.md"
    if module and not all_modules:
        # Append to existing review or create new
        if review_path.exists():
            existing = review_path.read_text(encoding="utf-8")
            result = existing + "\n\n---\n\n" + f"## 模块审查：{module}\n\n" + result
        _write(review_path, result)
        console.print(f"\n[bold]Coverage review complete for module: [cyan]{module}[/cyan][/bold]")
    else:
        _write(review_path, result)
        console.print(f"\n[bold]Coverage review complete for: [cyan]{feature}[/cyan][/bold]")


def _resolve_feature(project_dir: Path, output: Optional[str]) -> str:
    """Resolve feature name from -o param or config default."""
    if output:
        return output
    default = _get_default_feature(project_dir)
    if default:
        return default
    console.print("[red]Error: No -o specified and no default_feature in config.[/red]")
    console.print("[dim]Run 'testspec.analyze -o <feature>' first or specify -o.[/dim]")
    raise ValueError("feature not specified")


def _parse_modules_from_analysis(analysis_path: Path) -> list[dict]:
    """Parse modules from analysis.md content."""
    if not analysis_path.exists():
        return []
    content = analysis_path.read_text(encoding="utf-8")
    
    modules = []
    import re
    
    # Match module sections: ### 模块 X：模块名称 或 ### 模块 X: Module Name
    pattern = r"###\s+模块\s*\d*[:：]\s*([^\n]+)"
    matches = re.findall(pattern, content)
    
    for idx, name in enumerate(matches, 1):
        module_id = f"{idx:03d}"
        # Generate English name (simple conversion)
        english_name = name.strip().lower()
        english_name = re.sub(r'[^\w\s-]', '', english_name)
        english_name = re.sub(r'[\s]+', '-', english_name)
        modules.append({
            "id": module_id,
            "name": name.strip(),
            "english_name": english_name,
        })
    
    return modules


def _count_cases_by_module(cases_path: Path) -> dict[str, int]:
    """Count test cases per module from cases.md."""
    if not cases_path.exists():
        return {}
    content = cases_path.read_text(encoding="utf-8")
    import re
    
    counts = {}
    # Match module headers like ## 001-coupon-type-manager
    module_pattern = r"##\s+(\d{3}-[^\n]+)"
    case_pattern = r"###\s+TC-"
    
    modules = re.findall(module_pattern, content)
    for module in modules:
        # Count cases under this module
        module_start = content.find(f"## {module}")
        if module_start == -1:
            continue
        module_end = content.find("## ", module_start + 1)
        if module_end == -1:
            module_end = len(content)
        module_content = content[module_start:module_end]
        case_count = len(re.findall(case_pattern, module_content))
        counts[module] = case_count
    
    return counts


def list_modules(project_dir: Path, output: Optional[str] = None) -> None:
    """List all modules from analysis with progress status."""
    feature = _resolve_feature(project_dir, output)
    fd = _tests(project_dir) / feature
    
    analysis_path = fd / "analysis.md"
    if not analysis_path.exists():
        console.print(f"[red]Error: {analysis_path} not found. Run 'testspec.analyze -o {feature}' first.[/red]")
        return
    
    modules = _parse_modules_from_analysis(analysis_path)
    if not modules:
        console.print("[yellow]No modules found in analysis.md[/yellow]")
        return
    
    # Check progress
    strategy_exists = (fd / "strategy.md").exists()
    cases_path = fd / "cases.md"
    case_counts = _count_cases_by_module(cases_path) if cases_exists else {}
    review_exists = (fd / "review.md").exists()
    
    table = Table(title=f"模块清单：{feature}", border_style="cyan")
    table.add_column("编号", style="bold", justify="center")
    table.add_column("模块名称", style="cyan")
    table.add_column("用例数", justify="right")
    table.add_column("状态")
    
    total_cases = 0
    for m in modules:
        module_key = f"{m['id']}-{m['english_name']}"
        case_count = case_counts.get(module_key, 0)
        total_cases += case_count
        
        # Determine status
        if case_count > 0:
            status = "[green]✓ 已生成[/green]"
        elif strategy_exists:
            status = "[yellow]⏳ 策略就绪[/yellow]"
        else:
            status = "[dim]— 待处理[/dim]"
        
        table.add_row(
            m["id"],
            f"{m['name']}\n[dim]{m['english_name']}[/dim]",
            str(case_count) if case_count > 0 else "—",
            status
        )
    
    console.print(table)
    console.print(f"\n[dim]总计：{len(modules)} 个模块，{total_cases} 条用例[/dim]")


def status(project_dir: Path, output: Optional[str] = None) -> None:
    """Show the workflow status for a feature."""
    feature = _resolve_feature(project_dir, output)
    fd = _tests(project_dir) / feature
    stages = [
        ("1. Analyze", "analysis.md"),
        ("2. Strategy", "strategy.md"),
        ("3. Generate", "cases.md"),
        ("4. Review", "review.md"),
    ]

    table = Table(title=f"testspec status — {feature}", border_style="cyan")
    table.add_column("Stage", style="bold")
    table.add_column("File")
    table.add_column("Status")

    for label, filename in stages:
        path = fd / filename
        if path.exists():
            size = f"{path.stat().st_size:,} bytes"
            table.add_row(label, filename, f"[green]✓ Done[/green] ({size})")
        else:
            table.add_row(label, filename, "[dim]— Pending[/dim]")

    console.print(table)
