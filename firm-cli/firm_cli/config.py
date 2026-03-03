"""firm config — manage Firm ecosystem configuration.

Includes embedding model management for multilingual/French support:
    firm config set memory.model paraphrase-multilingual-MiniLM-L12-v2
    firm config models           # list recommended embedding models

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

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

# Recommended embedding models for various languages
RECOMMENDED_MODELS = {
    "all-MiniLM-L6-v2": {
        "lang": "English",
        "dim": 384,
        "speed": "fast",
        "note": "Default. Best speed/quality trade-off for English.",
    },
    "paraphrase-multilingual-MiniLM-L12-v2": {
        "lang": "50+ languages (incl. French)",
        "dim": 384,
        "speed": "fast",
        "note": "Recommended for French. Similar speed to default, multilingual.",
    },
    "BAAI/bge-m3": {
        "lang": "100+ languages",
        "dim": 1024,
        "speed": "medium",
        "note": "State-of-the-art multilingual. Higher quality, slower.",
    },
    "dangvantuan/sentence-camembert-large": {
        "lang": "French",
        "dim": 1024,
        "speed": "slow",
        "note": "French-specific. Best quality for French-only deployments.",
    },
    "OrdalieTech/Solon-embeddings-large-0.1": {
        "lang": "French",
        "dim": 1024,
        "speed": "slow",
        "note": "French-specific. Optimized for French legal/business texts.",
    },
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
    elif cmd == "models":
        return _config_models()
    else:
        console.print("[yellow]Usage: firm config set <key> <value> | firm config show | firm config models[/yellow]")
        return 0


def _config_set(key: str, value: str) -> int:
    """Set a configuration value."""
    config = _load_config()
    old = config.get(key, "(unset)")
    config[key] = value
    _save_config(config)
    console.print(f"  [green]✓[/green] {key}: {old} → [bold]{value}[/bold]")

    # Hint for model changes
    if key == "memory.model":
        if value in RECOMMENDED_MODELS:
            info = RECOMMENDED_MODELS[value]
            console.print(f"    [dim]{info['note']}[/dim]")
        else:
            console.print(f"    [yellow]Custom model. Run `firm config models` for recommended options.[/yellow]")
        console.print("    [dim]Restart servers for changes to take effect: firm stop && firm start[/dim]")
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


def _config_models() -> int:
    """Show recommended embedding models for memory.model."""
    config = _load_config()
    current = config.get("memory.model", DEFAULTS["memory.model"])

    table = Table(title="Recommended Embedding Models", border_style="cyan")
    table.add_column("Model", style="bold")
    table.add_column("Languages")
    table.add_column("Dim")
    table.add_column("Speed")
    table.add_column("Note")
    table.add_column("", style="green")

    for model_name, info in RECOMMENDED_MODELS.items():
        active = "← active" if model_name == current else ""
        table.add_row(
            model_name,
            info["lang"],
            str(info["dim"]),
            info["speed"],
            info["note"],
            active,
        )

    console.print(table)
    console.print(f"\n  Current model: [bold]{current}[/bold]")
    console.print("  Change: [bold]firm config set memory.model <model-name>[/bold]")
    console.print("\n  [dim]For French deployments, we recommend:[/dim]")
    console.print("    [bold]firm config set memory.model paraphrase-multilingual-MiniLM-L12-v2[/bold]")
    return 0
