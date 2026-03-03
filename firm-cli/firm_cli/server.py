"""firm start / stop / status — manage the MCP server lifecycle.

Supports two modes:
  - **unified** (default): 2 processes (openclaw-extensions :8012, memory-os-ai :8765)
  - **split** (`--split`): 4 processes by domain for large deployments
    - security  :8012  (security + gateway + runtime + advanced + config + compliance)
    - memory    :8013  (hebbian memory + memory audit + observability)
    - business  :8014  (delivery + orchestration + ecosystem + i18n + n8n + browser)
    - memory-os :8765  (memory-os-ai standalone)

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()

PIDFILE_DIR = Path.home() / ".firm"
OPENCLAW_PID = PIDFILE_DIR / "openclaw-extensions.pid"
MEMORY_PID = PIDFILE_DIR / "memory-os-ai.pid"

# Split-mode pidfiles (one per domain)
SPLIT_SECURITY_PID = PIDFILE_DIR / "split-security.pid"
SPLIT_MEMORY_PID = PIDFILE_DIR / "split-memory.pid"
SPLIT_BUSINESS_PID = PIDFILE_DIR / "split-business.pid"

# Domain definitions for split mode
SPLIT_DOMAINS = {
    "security": {
        "port": 8012,
        "pidfile": SPLIT_SECURITY_PID,
        "modules": [
            "security_audit", "gateway_hardening", "runtime_audit",
            "advanced_security", "config_migration", "spec_compliance",
            "prompt_security", "auth_compliance", "compliance_medium",
            "gateway_fleet",
        ],
        "description": "Security, compliance & gateway tools",
    },
    "memory": {
        "port": 8013,
        "pidfile": SPLIT_MEMORY_PID,
        "modules": [
            "hebbian_memory", "acp_bridge", "observability",
            "memory_audit", "skill_loader",
        ],
        "description": "Hebbian memory & observability tools",
    },
    "business": {
        "port": 8014,
        "pidfile": SPLIT_BUSINESS_PID,
        "modules": [
            "delivery_export", "agent_orchestration", "ecosystem_audit",
            "platform_audit", "i18n_audit", "n8n_bridge",
            "browser_audit", "a2a_bridge", "reliability_probe",
        ],
        "description": "Business, orchestration & integration tools",
    },
}


def _is_running(pidfile: Path) -> tuple[bool, int | None]:
    """Check if a process from a pidfile is still running."""
    if not pidfile.exists():
        return False, None
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)  # signal 0 = check if alive
        return True, pid
    except (ValueError, ProcessLookupError, PermissionError):
        pidfile.unlink(missing_ok=True)
        return False, None


def _health_check(url: str) -> dict | None:
    """Quick HTTP health check."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _heartbeat_check(endpoints: list[tuple[str, str]]) -> list[dict]:
    """Check heartbeat for multiple endpoints in parallel."""
    results = []
    for name, url in endpoints:
        health = _health_check(url)
        results.append({
            "name": name,
            "url": url,
            "alive": health is not None,
            "health": health,
        })
    return results


def _start_split_domain(domain: str, info: dict) -> tuple[bool, int | None]:
    """Start a single split-mode domain process."""
    pidfile = info["pidfile"]
    alive, pid = _is_running(pidfile)
    if alive:
        return True, pid
    try:
        env = os.environ.copy()
        env["FIRM_SPLIT_DOMAIN"] = domain
        env["FIRM_SPLIT_PORT"] = str(info["port"])
        env["FIRM_SPLIT_MODULES"] = ",".join(info["modules"])
        proc = subprocess.Popen(
            [sys.executable, "-m", "src.main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=env,
        )
        pidfile.write_text(str(proc.pid))
        return True, proc.pid
    except Exception:
        return False, None


def run_start(args: argparse.Namespace) -> int:
    """Start MCP servers."""
    PIDFILE_DIR.mkdir(parents=True, exist_ok=True)

    split = getattr(args, "split", False)

    if split:
        return _run_start_split()
    return _run_start_unified()


def _auto_install(package: str) -> bool:
    """Prompt the user and auto-install a missing pip package. Returns True on success."""
    try:
        answer = console.input(
            f"  [yellow]?[/yellow] {package} not found. Install now? [bold][Y/n][/bold] "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer in ("", "y", "yes"):
        console.print(f"  [dim]Installing {package}…[/dim]")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] {package} installed")
            return True
        console.print(f"  [red]✗[/red] pip install failed: {result.stderr.strip()[:200]}")
    else:
        console.print(f"  [dim]Skipped {package}[/dim]")
    return False


def _ensure_package(import_name: str, pip_name: str) -> bool:
    """Check if a package is importable; auto-install if missing. Returns True if available."""
    try:
        __import__(import_name)
        console.print(f"  [green]✓[/green] {pip_name} found")
        return True
    except ImportError:
        return _auto_install(pip_name)


def _run_start_unified() -> int:
    """Start in unified mode (2 processes)."""
    console.print(Panel("[bold cyan]firm start[/bold cyan] — unified mode", border_style="cyan"))

    # Check / auto-install mcp-openclaw-extensions
    has_mcp = _ensure_package("src.main", "mcp-openclaw-extensions")

    # Start openclaw-extensions
    alive, pid = _is_running(OPENCLAW_PID)
    if alive:
        console.print(f"  [dim]openclaw-extensions already running (PID {pid})[/dim]")
    elif has_mcp:
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "src.main"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            OPENCLAW_PID.write_text(str(proc.pid))
            console.print(f"  [green]✓[/green] openclaw-extensions started (PID {proc.pid})")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to start openclaw-extensions: {e}")
    else:
        console.print("  [red]✗[/red] openclaw-extensions skipped (not installed)")

    # Check / auto-install memory-os-ai
    has_mem = _ensure_package("memory_os_ai", "memory-os-ai")

    # Start memory-os-ai
    alive, pid = _is_running(MEMORY_PID)
    if alive:
        console.print(f"  [dim]memory-os-ai already running (PID {pid})[/dim]")
    elif has_mem:
        try:
            proc = subprocess.Popen(
                ["memory-os-ai", "--sse"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            MEMORY_PID.write_text(str(proc.pid))
            console.print(f"  [green]✓[/green] memory-os-ai started (PID {proc.pid})")
        except FileNotFoundError:
            console.print("  [red]✗[/red] memory-os-ai entry point not found after install")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to start memory-os-ai: {e}")
    else:
        console.print("  [red]✗[/red] memory-os-ai skipped (not installed)")

    return 0


def _run_start_split() -> int:
    """Start in split mode (4 processes — 3 domains + memory-os-ai)."""
    console.print(Panel(
        "[bold cyan]firm start --split[/bold cyan] — multi-domain mode",
        border_style="cyan",
    ))

    # Start each domain
    for domain, info in SPLIT_DOMAINS.items():
        ok, pid = _start_split_domain(domain, info)
        if ok and pid:
            console.print(
                f"  [green]✓[/green] {domain} domain started "
                f"(PID {pid}, :{info['port']}) — {info['description']}"
            )
        else:
            console.print(f"  [red]✗[/red] Failed to start {domain} domain")

    # Start memory-os-ai
    alive, pid = _is_running(MEMORY_PID)
    if alive:
        console.print(f"  [dim]memory-os-ai already running (PID {pid})[/dim]")
    else:
        try:
            proc = subprocess.Popen(
                ["memory-os-ai", "--sse"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            MEMORY_PID.write_text(str(proc.pid))
            console.print(f"  [green]✓[/green] memory-os-ai started (PID {proc.pid}, :8765)")
        except FileNotFoundError:
            console.print("  [yellow]![/yellow] memory-os-ai not installed")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to start memory-os-ai: {e}")

    console.print()
    console.print("  [dim]Endpoints:[/dim]")
    for domain, info in SPLIT_DOMAINS.items():
        console.print(f"    {domain:12s} → http://127.0.0.1:{info['port']}")
    console.print(f"    {'memory-os':12s} → http://127.0.0.1:8765")

    return 0


def run_stop() -> int:
    """Stop MCP servers (both unified and split mode)."""
    console.print(Panel("[bold cyan]firm stop[/bold cyan]", border_style="cyan"))

    # Stop unified PIDs
    for name, pidfile in [("openclaw-extensions", OPENCLAW_PID), ("memory-os-ai", MEMORY_PID)]:
        alive, pid = _is_running(pidfile)
        if alive and pid:
            try:
                os.kill(pid, signal.SIGTERM)
                pidfile.unlink(missing_ok=True)
                console.print(f"  [green]✓[/green] {name} stopped (PID {pid})")
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to stop {name}: {e}")
        else:
            console.print(f"  [dim]{name} not running[/dim]")

    # Stop split-mode PIDs
    for domain, info in SPLIT_DOMAINS.items():
        alive, pid = _is_running(info["pidfile"])
        if alive and pid:
            try:
                os.kill(pid, signal.SIGTERM)
                info["pidfile"].unlink(missing_ok=True)
                console.print(f"  [green]✓[/green] {domain} domain stopped (PID {pid})")
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to stop {domain}: {e}")

    return 0


def _build_status_table() -> Table:
    """Build the status table (shared by run_status and --watch)."""
    table = Table(title="Firm Ecosystem Status", border_style="cyan")
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("PID")
    table.add_column("Endpoint")
    table.add_column("Heartbeat")
    table.add_column("Details")

    # Unified mode — openclaw-extensions
    alive, pid = _is_running(OPENCLAW_PID)
    health = _health_check("http://127.0.0.1:8012/health") if alive else None
    if health:
        tools = health.get("tools", "?")
        version = health.get("version", "?")
        table.add_row(
            "mcp-openclaw-extensions",
            "[green]● running[/green]", str(pid),
            "http://127.0.0.1:8012", "[green]✓[/green]",
            f"{tools} tools, v{version}",
        )
    elif alive:
        table.add_row(
            "mcp-openclaw-extensions",
            "[yellow]● starting[/yellow]", str(pid),
            "http://127.0.0.1:8012", "[yellow]…[/yellow]", "",
        )
    else:
        table.add_row(
            "mcp-openclaw-extensions",
            "[red]● stopped[/red]", "-", "-", "-", "firm start",
        )

    # Unified mode — memory-os-ai
    alive2, pid2 = _is_running(MEMORY_PID)
    health2 = _health_check("http://127.0.0.1:8765/health") if alive2 else None
    if health2:
        tools2 = health2.get("tools", "?")
        table.add_row(
            "memory-os-ai",
            "[green]● running[/green]", str(pid2),
            "http://127.0.0.1:8765", "[green]✓[/green]",
            f"{tools2} tools",
        )
    elif alive2:
        table.add_row(
            "memory-os-ai",
            "[yellow]● starting[/yellow]", str(pid2),
            "http://127.0.0.1:8765", "[yellow]…[/yellow]", "",
        )
    else:
        table.add_row(
            "memory-os-ai",
            "[red]● stopped[/red]", "-", "-", "-",
            "pip install memory-os-ai",
        )

    # Split-mode domains
    for domain, info in SPLIT_DOMAINS.items():
        alive_d, pid_d = _is_running(info["pidfile"])
        if not alive_d:
            continue
        url = f"http://127.0.0.1:{info['port']}"
        health_d = _health_check(f"{url}/health")
        if health_d:
            tools_d = health_d.get("tools", "?")
            table.add_row(
                f"  └─ {domain}",
                "[green]● running[/green]", str(pid_d),
                url, "[green]✓[/green]",
                f"{tools_d} tools",
            )
        elif alive_d:
            table.add_row(
                f"  └─ {domain}",
                "[yellow]● starting[/yellow]", str(pid_d),
                url, "[yellow]…[/yellow]", "",
            )

    return table


def run_status(watch: bool = False, interval: int = 5) -> int:
    """Show ecosystem status. With watch=True, refresh every `interval` seconds."""
    if not watch:
        table = _build_status_table()
        console.print(table)
        return 0

    # --watch mode: live-refresh with Rich Live
    console.print("[dim]Press Ctrl+C to stop watching[/dim]\n")
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                table = _build_status_table()
                live.update(table)
                time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped watching.[/dim]")
    return 0
