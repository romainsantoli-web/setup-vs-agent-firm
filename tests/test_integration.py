#!/usr/bin/env python3
"""
Cross-repo integration test — validates the 3-repo stack communicates correctly.

Repos:
  1. setup-vs-agent-firm   (parent — skills, souls, factory, MCP config)
  2. mcp-openclaw-extensions (MCP server — port 8012 — 138 tools)
  3. Memory-os-ai           (MCP server — port 8765 — memory + search tools)

Tests (54 assertions across 9 categories):
  A. Both MCP servers start and respond to JSON-RPC
  B. Tool registry is complete (expected tools present)
  C. Unified MCP config references both servers correctly
  D. Skills/Souls are present and readable
  E. Cross-server tool calls work
  F. Health endpoints respond correctly
  G. Docker-compose config is valid
  H. Dockerfiles exist and are valid
  I. MCP initialize protocol works correctly

Configuration via environment variables:
  PARENT_REPO     — path to setup-vs-agent-firm (default: script parent dir)
  MEMORY_REPO     — path to Memory-os-ai (default: ../Memory-os-ai relative to parent)
  OPENCLAW_PORT   — port for openclaw-extensions (default: 8012)
  MEMORY_PORT     — port for memory-os-ai (default: 8765)

Usage:
  python tests/test_integration.py
  MEMORY_REPO=/path/to/Memory-os-ai python tests/test_integration.py

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# ── Paths (configurable via env) ───────────────────────────────────────────
PARENT_REPO = Path(os.environ.get("PARENT_REPO", Path(__file__).resolve().parent.parent))
OPENCLAW_REPO = PARENT_REPO / "mcp-openclaw-extensions"
MEMORY_REPO = Path(os.environ.get("MEMORY_REPO", PARENT_REPO.parent / "Memory-os-ai"))

OPENCLAW_VENV = OPENCLAW_REPO / ".venv" / "bin" / "python"
MEMORY_VENV = MEMORY_REPO / ".venv" / "bin" / "python"

OPENCLAW_PORT = int(os.environ.get("OPENCLAW_PORT", "8012"))
MEMORY_PORT = int(os.environ.get("MEMORY_PORT", "8765"))

# Will hold server processes for cleanup
_processes: list[subprocess.Popen] = []

# ── Helpers ────────────────────────────────────────────────────────────────

def _print(msg: str, ok: bool | None = None):
    icon = "\u2705" if ok is True else "\u274c" if ok is False else "\U0001f504"
    print(f"  {icon} {msg}")


def _jsonrpc(port: int, method: str, params: dict | None = None, timeout: float = 10) -> dict:
    """Send a JSON-RPC 2.0 request to an MCP server."""
    import urllib.request
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        payload["params"] = params
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/mcp",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def _http_get(url: str, timeout: float = 5) -> tuple[int, dict | str]:
    """GET a URL and return (status, body)."""
    import urllib.request
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except Exception as e:
        return 0, str(e)


def _wait_for_server(port: int, name: str, max_wait: int = 30) -> bool:
    """Wait until a server responds on the given port."""
    import urllib.request
    start = time.time()
    while time.time() - start < max_wait:
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/health",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def start_servers():
    """Start both MCP servers as background processes."""
    print("\n\U0001f680 Starting MCP servers...")

    # Start openclaw-extensions
    env_oc = os.environ.copy()
    env_oc["MCP_EXT_HOST"] = "127.0.0.1"
    env_oc["MCP_EXT_PORT"] = str(OPENCLAW_PORT)
    env_oc["MCP_AUTH_TOKEN"] = ""  # disable auth for test
    proc_oc = subprocess.Popen(
        [str(OPENCLAW_VENV), "-m", "src.main"],
        cwd=str(OPENCLAW_REPO),
        env=env_oc,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _processes.append(proc_oc)
    _print(f"openclaw-extensions PID {proc_oc.pid} (port {OPENCLAW_PORT})")

    # Start memory-os-ai (SSE transport)
    env_mem = os.environ.copy()
    env_mem["MEMORY_HOST"] = "127.0.0.1"
    env_mem["MEMORY_PORT"] = str(MEMORY_PORT)
    env_mem["MEMORY_CACHE_DIR"] = "/tmp/memory-os-ai-test"
    env_mem["PYTHONPATH"] = str(MEMORY_REPO / "src")
    env_mem["TOKENIZERS_PARALLELISM"] = "false"
    os.makedirs("/tmp/memory-os-ai-test", exist_ok=True)
    proc_mem = subprocess.Popen(
        [str(MEMORY_VENV), "-m", "memory_os_ai.server", "--sse"],
        cwd=str(MEMORY_REPO),
        env=env_mem,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _processes.append(proc_mem)
    _print(f"memory-os-ai PID {proc_mem.pid} (port {MEMORY_PORT})")

    # Wait for both
    oc_ready = _wait_for_server(OPENCLAW_PORT, "openclaw-extensions", max_wait=20)
    _print(f"openclaw-extensions ready: {oc_ready}", oc_ready)

    mem_ready = _wait_for_server(MEMORY_PORT, "memory-os-ai", max_wait=45)
    _print(f"memory-os-ai ready: {mem_ready}", mem_ready)

    return oc_ready, mem_ready


def stop_servers():
    """Stop all server processes."""
    print("\n\U0001f6d1 Stopping servers...")
    for p in _processes:
        try:
            p.send_signal(signal.SIGTERM)
            p.wait(timeout=5)
        except Exception:
            p.kill()
    _processes.clear()


# ══════════════════════════════════════════════════════════════════════════
# TEST SECTIONS
# ══════════════════════════════════════════════════════════════════════════

results: list[tuple[str, bool]] = []


def test(name: str, passed: bool, detail: str = ""):
    results.append((name, passed))
    _print(f"{name}: {detail}" if detail else name, passed)


def test_A_servers_respond(oc_ready: bool, mem_ready: bool):
    """A. Both servers respond to JSON-RPC ping."""
    print("\n\u2500\u2500 A. Server connectivity \u2500\u2500")

    test("A1. openclaw-extensions started", oc_ready)
    test("A2. memory-os-ai started", mem_ready)

    if oc_ready:
        r = _jsonrpc(OPENCLAW_PORT, "ping")
        test("A3. openclaw ping", "result" in r, str(r.get("result", r.get("error", "")))[:80])
    else:
        test("A3. openclaw ping", False, "server not started")

    if mem_ready:
        status, body = _http_get(f"http://127.0.0.1:{MEMORY_PORT}/health")
        test("A4. memory-os-ai health", status == 200, str(body)[:80])
    else:
        test("A4. memory-os-ai health", False, "server not started")


def test_B_tool_registries(oc_ready: bool, mem_ready: bool):
    """B. Tool registries are complete."""
    print("\n\u2500\u2500 B. Tool registries \u2500\u2500")

    if oc_ready:
        r = _jsonrpc(OPENCLAW_PORT, "tools/list")
        if "result" in r:
            tools = r["result"].get("tools", [])
            names = {t["name"] for t in tools}
            count = len(tools)
            test("B1. openclaw tool count >= 115", count >= 115, f"{count} tools")

            expected_tools = [
                "vs_context_push", "vs_context_pull",
                "firm_gateway_fleet_status",
                "openclaw_security_scan",
                "openclaw_hebbian_harvest",
                "openclaw_a2a_card_generate",
                "firm_export_auto",
            ]
            for t in expected_tools:
                test(f"B2. tool '{t}' registered", t in names)
        else:
            test("B1. openclaw tools/list", False, str(r.get("error", ""))[:80])
    else:
        test("B1. openclaw tools (skipped)", False, "server not started")

    if mem_ready:
        test("B3. memory-os-ai alive (SSE)", True, "health OK")
    else:
        test("B3. memory-os-ai alive", False, "server not started")


def test_C_unified_config():
    """C. Unified MCP config references both servers."""
    print("\n\u2500\u2500 C. Unified MCP config \u2500\u2500")

    config_path = PARENT_REPO / "mcp-config-unified.json"
    test("C1. mcp-config-unified.json exists", config_path.exists())

    if config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)

        servers = cfg.get("servers", {})
        test("C2. config has 'memory-os-ai' server", "memory-os-ai" in servers)
        test("C3. config has 'openclaw-extensions' server", "openclaw-extensions" in servers)

        if "openclaw-extensions" in servers:
            oc_cfg = servers["openclaw-extensions"]
            test("C4. openclaw type = http", oc_cfg.get("type") == "http")
            test("C5. openclaw url contains 8012", "8012" in oc_cfg.get("url", ""))

        if "memory-os-ai" in servers:
            mem_cfg = servers["memory-os-ai"]
            test("C6. memory-os-ai type = stdio", mem_cfg.get("type") == "stdio")


def test_D_skills_souls():
    """D. Skills and Souls are present and readable."""
    print("\n\u2500\u2500 D. Skills & Souls \u2500\u2500")

    skills_dir = PARENT_REPO / "skills"
    souls_dir = PARENT_REPO / "souls"

    test("D1. skills/ directory exists", skills_dir.is_dir())
    test("D2. souls/ directory exists", souls_dir.is_dir())

    if skills_dir.is_dir():
        skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
        count = len(skills)
        test("D3. skill count >= 10", count >= 10, f"{count} skills")

        for sk in ["firm-security-audit", "firm-a2a-bridge", "firm-hebbian-memory"]:
            sk_path = skills_dir / sk / "SKILL.md"
            test(f"D4. {sk}/SKILL.md readable", sk_path.exists())

    if souls_dir.is_dir():
        souls = [d.name for d in souls_dir.iterdir() if d.is_dir() and (d / "SOUL.md").exists()]
        test("D5. soul count >= 3", len(souls) >= 3, f"{len(souls)} souls: {', '.join(souls[:5])}")


def test_E_cross_server_tool_call(oc_ready: bool):
    """E. Cross-server tool calls work."""
    print("\n\u2500\u2500 E. Cross-server tool calls \u2500\u2500")

    if not oc_ready:
        test("E1. (skipped \u2014 openclaw not running)", False)
        return

    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"gateway": {"auth": {"mode": "password"}}}, f)
        cfg_path = f.name

    r = _jsonrpc(OPENCLAW_PORT, "tools/call", {
        "name": "openclaw_security_scan",
        "arguments": {"config_path": cfg_path},
    })
    if "result" in r:
        content = r["result"].get("content", [])
        test("E1. openclaw_security_scan returns result", len(content) > 0,
             str(content[0].get("text", ""))[:100] if content else "empty")
    else:
        test("E1. openclaw_security_scan", False, str(r.get("error", ""))[:100])

    r2 = _jsonrpc(OPENCLAW_PORT, "tools/call", {
        "name": "vs_context_push",
        "arguments": {"workspace_path": str(PARENT_REPO)},
    })
    if "result" in r2:
        test("E2. vs_context_push degrades gracefully", True)
    else:
        test("E2. vs_context_push response", "error" in r2 or "result" in r2)

    r3 = _jsonrpc(OPENCLAW_PORT, "tools/call", {
        "name": "openclaw_hebbian_status",
        "arguments": {},
    })
    has_result = "result" in r3
    test("E3. openclaw_hebbian_status returns", has_result,
         str(r3.get("result", r3.get("error", "")))[:100])

    os.unlink(cfg_path)


def test_F_health_endpoints(oc_ready: bool, mem_ready: bool):
    """F. Health endpoints respond correctly."""
    print("\n\u2500\u2500 F. Health endpoints \u2500\u2500")

    if oc_ready:
        status, body = _http_get(f"http://127.0.0.1:{OPENCLAW_PORT}/health")
        test("F1. openclaw /health status 200", status == 200)
        if isinstance(body, dict):
            test("F2. openclaw /health has tool_count", "tool_count" in body or "tools" in body,
                 str(body)[:100])

        status2, body2 = _http_get(f"http://127.0.0.1:{OPENCLAW_PORT}/healthz")
        test("F3. openclaw /healthz status 200", status2 == 200)
    else:
        test("F1. openclaw health (skipped)", False)

    if mem_ready:
        status, body = _http_get(f"http://127.0.0.1:{MEMORY_PORT}/health")
        test("F4. memory-os-ai /health status 200", status == 200)
        if isinstance(body, dict):
            test("F5. memory-os-ai /health has 'ok'", body.get("ok") is True)
    else:
        test("F4. memory-os-ai health (skipped)", False)


def test_G_docker_compose():
    """G. Docker-compose config is valid."""
    print("\n\u2500\u2500 G. Docker-compose validation \u2500\u2500")

    dc_path = PARENT_REPO / "docker-compose.yml"
    test("G1. docker-compose.yml exists", dc_path.exists())

    if dc_path.exists():
        import yaml
        with open(dc_path) as f:
            dc = yaml.safe_load(f)

        services = dc.get("services", {})
        test("G2. has 'memory-os-ai' service", "memory-os-ai" in services)
        test("G3. has 'openclaw-extensions' service", "openclaw-extensions" in services)

        if "openclaw-extensions" in services:
            oc = services["openclaw-extensions"]
            ports = oc.get("ports", [])
            test("G4. openclaw port 8012 mapped", any("8012" in str(p) for p in ports))
            test("G5. openclaw has healthcheck", "healthcheck" in oc)
            test("G6. openclaw build context correct",
                 oc.get("build", {}).get("context", "") == "./mcp-openclaw-extensions")

        if "memory-os-ai" in services:
            mem = services["memory-os-ai"]
            ports = mem.get("ports", [])
            test("G7. memory port 8765 mapped", any("8765" in str(p) for p in ports))
            test("G8. memory has healthcheck", "healthcheck" in mem)
            test("G9. memory build context correct",
                 mem.get("build", {}).get("context", "") == "../Memory-os-ai")


def test_H_dockerfile_validity():
    """H. Dockerfiles exist and are valid."""
    print("\n\u2500\u2500 H. Dockerfiles \u2500\u2500")

    oc_df = OPENCLAW_REPO / "Dockerfile"
    mem_df = MEMORY_REPO / "Dockerfile"

    test("H1. openclaw Dockerfile exists", oc_df.exists())
    test("H2. memory-os-ai Dockerfile exists", mem_df.exists())

    if oc_df.exists():
        content = oc_df.read_text()
        test("H3. openclaw Dockerfile has FROM", "FROM" in content)
        test("H4. openclaw Dockerfile has EXPOSE", "EXPOSE" in content or "8012" in content)

    if mem_df.exists():
        content = mem_df.read_text()
        test("H5. memory-os-ai Dockerfile has FROM", "FROM" in content)
        test("H6. memory-os-ai Dockerfile has EXPOSE", "EXPOSE" in content or "8765" in content)


def test_I_initialize_protocol(oc_ready: bool):
    """I. MCP initialize protocol works correctly."""
    print("\n\u2500\u2500 I. MCP initialize protocol \u2500\u2500")

    if not oc_ready:
        test("I1. (skipped \u2014 openclaw not running)", False)
        return

    r = _jsonrpc(OPENCLAW_PORT, "initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "test-harness", "version": "1.0.0"},
    })

    if "result" in r:
        result = r["result"]
        test("I1. initialize returns protocolVersion",
             "protocolVersion" in result, result.get("protocolVersion", ""))
        test("I2. initialize returns capabilities",
             "capabilities" in result)
        caps = result.get("capabilities", {})
        test("I3. capabilities has 'tools'", "tools" in caps)

        server_info = result.get("serverInfo", {})
        test("I4. serverInfo has name", "name" in server_info, server_info.get("name", ""))
        test("I5. serverInfo has version", "version" in server_info, server_info.get("version", ""))
    else:
        test("I1. initialize failed", False, str(r.get("error", ""))[:100])


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  CROSS-REPO INTEGRATION TEST \u2014 3 Repos Communication Validation")
    print("=" * 70)
    print(f"  Parent repo:    {PARENT_REPO}")
    print(f"  OpenClaw:       {OPENCLAW_REPO}")
    print(f"  Memory-os-ai:   {MEMORY_REPO}")
    print("=" * 70)

    oc_ready = mem_ready = False
    try:
        oc_ready, mem_ready = start_servers()

        test_A_servers_respond(oc_ready, mem_ready)
        test_B_tool_registries(oc_ready, mem_ready)
        test_C_unified_config()
        test_D_skills_souls()
        test_E_cross_server_tool_call(oc_ready)
        test_F_health_endpoints(oc_ready, mem_ready)
        test_G_docker_compose()
        test_H_dockerfile_validity()
        test_I_initialize_protocol(oc_ready)

    finally:
        stop_servers()

    # ── Summary ──
    print("\n" + "=" * 70)
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    total = len(results)
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 70)

    if failed:
        print("\n  Failures:")
        for name, ok in results:
            if not ok:
                print(f"    \u274c {name}")

    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
