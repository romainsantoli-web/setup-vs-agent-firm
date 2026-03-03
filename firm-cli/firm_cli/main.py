"""firm CLI — unified entry point for the Firm AI Agent ecosystem.

Usage:
    firm init [--sector SECTOR] [--size SIZE] [--stack STACK] [--output DIR]
    firm start [--split]
    firm stop
    firm status
    firm memory status
    firm memory analyze
    firm config set <key> <value>
    firm --version
    firm --help
"""

from __future__ import annotations

import argparse
import sys

from firm_cli import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firm",
        description="Create, start, and manage AI agent firms with inter-session Hebbian memory.",
        epilog="Documentation: https://github.com/romainsantoli-web/firm-ecosystem",
    )
    parser.add_argument("--version", action="version", version=f"firm-cli {__version__}")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── firm init ────────────────────────────────────────────
    p_init = sub.add_parser("init", help="Generate a new AI agent firm")
    p_init.add_argument(
        "--sector",
        default="generic",
        choices=[
            "generic", "legal", "medtech", "ecommerce", "fintech", "saas",
            "manufacturing", "education", "realestate", "logistics",
            "media", "automotive", "energy", "hr", "consulting",
        ],
        help="Industry sector (default: generic)",
    )
    p_init.add_argument(
        "--stack",
        default="typescript",
        choices=["typescript", "python", "java", "dotnet", "go", "rust", "mixed"],
        help="Tech stack (default: typescript)",
    )
    p_init.add_argument(
        "--size",
        default="startup",
        choices=["startup", "scaleup", "enterprise"],
        help="Firm size: startup (4 depts), scaleup (12), enterprise (18)",
    )
    p_init.add_argument("--output", "-o", default=".", help="Output directory (default: .)")
    p_init.add_argument("--name", default=None, help="Firm name (default: auto from sector)")
    p_init.add_argument("--lang", default="en", choices=["en", "fr"], help="Language (default: en)")
    p_init.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files")

    # ── firm start ───────────────────────────────────────────
    p_start = sub.add_parser("start", help="Start the MCP servers (openclaw-extensions + memory)")
    p_start.add_argument("--split", action="store_true", help="Run in split mode (multi-process by domain)")

    # ── firm stop ────────────────────────────────────────────
    sub.add_parser("stop", help="Stop the MCP servers")

    # ── firm status ──────────────────────────────────────────
    p_status = sub.add_parser("status", help="Show status of all ecosystem components")
    p_status.add_argument("--watch", "-w", action="store_true", help="Live refresh every 5 seconds")
    p_status.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds (default: 5)")

    # ── firm memory ──────────────────────────────────────────
    p_mem = sub.add_parser("memory", help="Manage inter-session Hebbian memory")
    mem_sub = p_mem.add_subparsers(dest="memory_command")
    mem_sub.add_parser("status", help="Show memory dashboard (weights, drift, sessions)")
    mem_sub.add_parser("analyze", help="Run Hebbian analysis (clustering + weight update)")
    p_mem_export = mem_sub.add_parser("export", help="Export memory to a portable JSON file")
    p_mem_export.add_argument("--output", "-o", default="firm-memory-export.json", help="Output file")
    p_mem_import = mem_sub.add_parser("import", help="Import memory from a JSON export file")
    p_mem_import.add_argument("source", help="Path to the export file")
    p_mem_import.add_argument("--merge", action="store_true", help="Merge rules instead of replacing")

    # ── firm config ──────────────────────────────────────────
    p_cfg = sub.add_parser("config", help="Manage firm configuration")
    cfg_sub = p_cfg.add_subparsers(dest="config_command")
    p_cfg_set = cfg_sub.add_parser("set", help="Set a configuration value")
    p_cfg_set.add_argument("key", help="Config key (e.g. memory.backend)")
    p_cfg_set.add_argument("value", help="Config value (e.g. sqlite)")
    cfg_sub.add_parser("show", help="Show current configuration")
    cfg_sub.add_parser("models", help="List recommended embedding models for Hebbian memory")

    return parser


def cli(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "init":
        from firm_cli.factory import run_init
        return run_init(args)

    if args.command == "start":
        from firm_cli.server import run_start
        return run_start(args)

    if args.command == "stop":
        from firm_cli.server import run_stop
        return run_stop()

    if args.command == "status":
        from firm_cli.server import run_status
        return run_status(
            watch=getattr(args, "watch", False),
            interval=getattr(args, "interval", 5),
        )

    if args.command == "memory":
        from firm_cli.memory import run_memory
        return run_memory(args)

    if args.command == "config":
        from firm_cli.config import run_config
        return run_config(args)

    parser.print_help()
    return 0


def main() -> None:
    sys.exit(cli())


if __name__ == "__main__":
    main()
