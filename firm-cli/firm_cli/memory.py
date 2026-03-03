"""firm memory — Hebbian memory dashboard, analysis, export/import commands."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

_EXPORT_VERSION = "1.0.0"
_EXPORT_MAGIC = "firm-memory-export"


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
    rules = []
    content = claude_md.read_text(encoding="utf-8")
    # Pattern: [0.94] Rule description
    for match in re.finditer(r"\[(\d+\.\d+)\]\s+(.+)", content):
        weight = float(match.group(1))
        desc = match.group(2).strip()
        rules.append({"weight": weight, "description": desc})
    return sorted(rules, key=lambda r: r["weight"], reverse=True)


def _find_session_logs() -> list[Path]:
    """Find JSONL session logs in the workspace."""
    cwd = Path.cwd()
    patterns = ["**/*.jsonl", ".firm/sessions/*.jsonl", "workspace/sessions/*.jsonl"]
    found: list[Path] = []
    for pattern in patterns:
        found.extend(cwd.glob(pattern))
    return sorted(set(found))


def run_memory(args: argparse.Namespace) -> int:
    """Entry point for `firm memory` commands."""
    cmd = getattr(args, "memory_command", None)

    if cmd == "status":
        return _memory_status()
    elif cmd == "analyze":
        return _memory_analyze()
    elif cmd == "export":
        output = getattr(args, "output", None) or "firm-memory-export.json"
        return _memory_export(Path(output))
    elif cmd == "import":
        source = getattr(args, "source", None)
        if not source:
            console.print("[red]Usage: firm memory import <file>[/red]")
            return 1
        merge = getattr(args, "merge", False)
        return _memory_import(Path(source), merge=merge)
    else:
        console.print("[yellow]Usage: firm memory status | analyze | export | import[/yellow]")
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
            resp.read()  # validate server is reachable
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
                "name": "firm_hebbian_analyze",
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


def _memory_export(output: Path) -> int:
    """Export memory state to a portable JSON file."""
    claude_md = _find_claude_md()
    if not claude_md:
        console.print("[yellow]No CLAUDE.md found. Nothing to export.[/yellow]")
        return 1

    rules = _parse_layer2_rules(claude_md)
    sessions = _find_session_logs()

    # Read full CLAUDE.md content for layer backup
    content = claude_md.read_text(encoding="utf-8")

    # Build export payload
    export_data = {
        "magic": _EXPORT_MAGIC,
        "version": _EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": str(claude_md),
        "memory": {
            "layer2_rules": rules,
            "layer2_count": len(rules),
            "claude_md_hash": str(hash(content)),
            "claude_md_size_bytes": len(content.encode("utf-8")),
        },
        "sessions": {
            "count": len(sessions),
            "paths": [str(s) for s in sessions],
        },
        "claude_md_content": content,
    }

    # Read session logs if they exist (include up to 100 sessions)
    session_data: list[dict] = []
    for s in sessions[:100]:
        try:
            lines = s.read_text(encoding="utf-8").strip().split("\n")
            entries = [json.loads(line) for line in lines if line.strip()]
            session_data.append({
                "path": str(s),
                "entries_count": len(entries),
                "entries": entries[:500],  # cap per session
            })
        except Exception:
            pass
    export_data["session_data"] = session_data

    output.write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
    size_kb = output.stat().st_size / 1024

    console.print(Panel(
        f"[bold]File[/bold]: {output}\n"
        f"[bold]Size[/bold]: {size_kb:.1f} KB\n"
        f"[bold]Rules[/bold]: {len(rules)} Layer 2 rules\n"
        f"[bold]Sessions[/bold]: {len(sessions)} JSONL files\n"
        f"[bold]Format[/bold]: {_EXPORT_MAGIC} v{_EXPORT_VERSION}",
        title="[bold green]Memory Exported[/bold green]",
        border_style="green",
    ))
    return 0


def _memory_import(source: Path, merge: bool = False) -> int:
    """Import memory state from a portable JSON file."""
    if not source.exists():
        console.print(f"[red]File not found: {source}[/red]")
        return 1

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        return 1

    if data.get("magic") != _EXPORT_MAGIC:
        console.print("[red]Not a valid firm memory export file.[/red]")
        return 1

    claude_md = _find_claude_md()
    if not claude_md:
        # Create claude.md in current directory
        claude_md = Path.cwd() / "CLAUDE.md"

    rules_imported = data.get("memory", {}).get("layer2_rules", [])
    content_imported = data.get("claude_md_content", "")

    if merge and claude_md.exists():
        # Merge: add new rules that don't exist yet
        existing_rules = _parse_layer2_rules(claude_md)
        existing_descs = {r["description"].lower() for r in existing_rules}
        new_rules = [r for r in rules_imported if r["description"].lower() not in existing_descs]

        if new_rules:
            existing_content = claude_md.read_text(encoding="utf-8")
            rules_block = "\n".join(
                f"[{r['weight']:.2f}] {r['description']}" for r in new_rules
            )
            merged = existing_content.rstrip() + "\n\n" + rules_block + "\n"
            # Backup before modifying
            backup = claude_md.with_suffix(".md.bak")
            shutil.copy2(claude_md, backup)
            claude_md.write_text(merged, encoding="utf-8")
            console.print(Panel(
                f"[bold]Merged[/bold]: {len(new_rules)} new rules\n"
                f"[bold]Skipped[/bold]: {len(rules_imported) - len(new_rules)} duplicates\n"
                f"[bold]Backup[/bold]: {backup}",
                title="[bold green]Memory Merged[/bold green]",
                border_style="green",
            ))
        else:
            console.print("[dim]No new rules to merge — all rules already exist.[/dim]")
    else:
        if not content_imported:
            console.print("[red]Export file has no CLAUDE.md content to restore.[/red]")
            return 1
        # Full replace with backup
        if claude_md.exists():
            backup = claude_md.with_suffix(".md.bak")
            shutil.copy2(claude_md, backup)
            console.print(f"  Backed up existing CLAUDE.md to {backup}")
        claude_md.write_text(content_imported, encoding="utf-8")
        console.print(Panel(
            f"[bold]File[/bold]: {claude_md}\n"
            f"[bold]Rules[/bold]: {len(rules_imported)} Layer 2 rules restored\n"
            f"[bold]Source[/bold]: {source}",
            title="[bold green]Memory Imported[/bold green]",
            border_style="green",
        ))

    # Import session data if present
    session_data = data.get("session_data", [])
    if session_data:
        sessions_dir = Path.cwd() / ".firm" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        imported = 0
        for sd in session_data:
            name = Path(sd["path"]).name
            dest = sessions_dir / name
            if not dest.exists():
                lines = [json.dumps(e) for e in sd.get("entries", [])]
                dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
                imported += 1
        if imported:
            console.print(f"  [green]✓[/green] Imported {imported} session logs to {sessions_dir}")

    return 0