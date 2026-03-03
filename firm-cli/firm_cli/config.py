"""firm config — manage Firm ecosystem configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

CONFIG_FILE = Path.home() / ".firm" / "config.json"

DEFAULTS = {
    "memory.backend": "sqlite",
    "memory.model": "all-MiniLM-L6-v2",
    "server.host": "127.0.0.1",
    "server.openclaw_port": "8012",
    "server.memory_port": "8765",
}


def _load_config() -> dict:
    """Load config from ~/.firm/config.json, falling back to defaults."""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULTS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULTS)


def _save_config(config: dict) -> None:
    """Save config to ~/.firm/config.json."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def run_config(args: argparse.Namespace) -> int:
    """Entry point for `firm config` commands."""
    cmd = getattr(args, "config_command", None)

    if cmd == "set":
        return _config_set(args.key, args.value)
    elif cmd == "show":
        return _config_show()
    else:
        console.print("[yellow]Usage: firm config set <key> <value> | firm config show[/yellow]")
        return 0


def _config_set(key: str, value: str) -> int:
    """Set a configuration value."""
    config = _load_config()
    old = config.get(key, "(unset)")
    config[key] = value
    _save_config(config)
    console.print(f"  [green]✓[/green] {key}: {old} → [bold]{value}[/bold]")
    return 0


def _config_show() -> int:
    """Show current configuration."""
    config = _load_config()
    table = Table(title="Firm Configuration", border_style="cyan")
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_column("Source")

    saved = {}
    if CONFIG_FILE.exists():
        try:
            saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    for key, value in sorted(config.items()):
        source = "[green]config[/green]" if key in saved else "[dim]default[/dim]"
        table.add_row(key, str(value), source)

    console.print(table)
    console.print(f"\n  [dim]Config file: {CONFIG_FILE}[/dim]")
    return 0
