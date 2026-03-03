"""firm memory — Hebbian memory dashboard and analysis commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def _find_claude_md() -> Path | None:
    """Find CLAUDE.md in current directory or parents."""
    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        candidate = p / "CLAUDE.md"
        if candidate.exists():
            return candidate
        if (p / ".git").exists():
            break  # stop at repo root
    return None


def _parse_layer2_rules(claude_md: Path) -> list[dict]:
    """Extract Layer 2 rules with weights from CLAUDE.md."""
    import re
    rules = []
    content = claude_md.read_text(encoding="utf-8")
    # Pattern: [0.94] Rule description
    for match in re.finditer(r"\[(\d+\.\d+)\]\s+(.+)", content):
        weight = float(match.group(1))
        desc = match.group(2).strip()
        rules.append({"weight": weight, "description": desc})
    return sorted(rules, key=lambda r: r["weight"], reverse=True)


def run_memory(args: argparse.Namespace) -> int:
    """Entry point for `firm memory` commands."""
    cmd = getattr(args, "memory_command", None)

    if cmd == "status":
        return _memory_status()
    elif cmd == "analyze":
        return _memory_analyze()
    else:
        console.print("[yellow]Usage: firm memory status | firm memory analyze[/yellow]")
        return 0


def _memory_status() -> int:
    """Display Hebbian memory dashboard."""
    claude_md = _find_claude_md()
    if not claude_md:
        console.print("[yellow]No CLAUDE.md found. Run `firm init` first.[/yellow]")
        return 1

    rules = _parse_layer2_rules(claude_md)

    console.print(Panel(
        f"[bold]CLAUDE.md[/bold]: {claude_md}\n"
        f"[bold]Layer 2 rules[/bold]: {len(rules)}",
        title="[bold cyan]Hebbian Memory Status[/bold cyan]",
        border_style="cyan",
    ))

    if not rules:
        console.print("[dim]No weighted rules found in Layer 2. Memory will grow as you work.[/dim]")
        return 0

    table = Table(title="Layer 2 — Consolidated Patterns", border_style="cyan")
    table.add_column("Weight", justify="right", style="bold")
    table.add_column("Status")
    table.add_column("Rule")

    for r in rules:
        w = r["weight"]
        if w >= 0.8:
            status = "[green]● strong[/green]"
        elif w >= 0.4:
            status = "[yellow]● emerging[/yellow]"
        elif w >= 0.1:
            status = "[dim]● weak[/dim]"
        else:
            status = "[red]● atrophy[/red]"
        table.add_row(f"{w:.2f}", status, r["description"])

    console.print(table)

    # Summary
    strong = sum(1 for r in rules if r["weight"] >= 0.8)
    emerging = sum(1 for r in rules if 0.4 <= r["weight"] < 0.8)
    atrophy = sum(1 for r in rules if r["weight"] < 0.1)
    if atrophy:
        console.print(f"\n  [red]{atrophy} rule(s) in atrophy[/red] — consider removal")
    if strong:
        promo = [r for r in rules if r["weight"] >= 0.90]
        if promo:
            console.print(f"  [green]{len(promo)} rule(s) eligible for CORE promotion[/green]")

    return 0


def _memory_analyze() -> int:
    """Run Hebbian analysis (requires analysis extras)."""
    try:
        # Check if MCP server is reachable
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8012/health", timeout=3) as resp:
            health = json.loads(resp.read())
    except Exception:
        console.print("[yellow]MCP server not reachable. Start with: firm start[/yellow]")
        console.print("[dim]Analysis requires mcp-openclaw-extensions running on port 8012[/dim]")
        return 1

    console.print(Panel(
        "Hebbian analysis calls the MCP server to:\n"
        "  1. Load sessions from the last 90 days\n"
        "  2. Compute co-activation patterns\n"
        "  3. Update Layer 2 weights\n"
        "  4. Propose new patterns if frequency > 3\n"
        "  5. Flag rules in atrophy (weight < 0.10)\n",
        title="[bold cyan]Hebbian Analysis[/bold cyan]",
        border_style="cyan",
    ))

    # Call the MCP tool via HTTP
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "openclaw_hebbian_analyze",
                "arguments": {"since_days": 90},
            },
        }).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:8012/mcp",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        if "result" in result:
            console.print("[green]✓ Analysis complete[/green]")
            console.print_json(json.dumps(result["result"], indent=2))
        else:
            console.print(f"[yellow]Server response: {result}[/yellow]")
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        return 1

    return 0
