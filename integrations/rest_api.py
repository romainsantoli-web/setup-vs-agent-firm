"""REST API wrapper — HTTP endpoints wrapping key MCP tools for non-MCP clients.

Provides a RESTful interface to the most commonly used MCP tools,
enabling integration from any HTTP client (curl, Postman, CI pipelines, etc.)
without needing MCP protocol knowledge.

Usage:
    python -m integrations.rest_api                     # Start on :8080
    python -m integrations.rest_api --port 9090         # Custom port
    FIRM_MCP_URL=http://host:8012 python -m integrations.rest_api

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

MCP_URL = os.getenv("FIRM_MCP_URL", "http://127.0.0.1:8012")
API_PORT = int(os.getenv("FIRM_REST_PORT", "8080"))

# ── MCP client helper ────────────────────────────────────────────────────────

_rpc_id = 0


def _mcp_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call an MCP tool via JSON-RPC over HTTP."""
    global _rpc_id
    _rpc_id += 1
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": _rpc_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }).encode()
    req = urllib.request.Request(
        f"{MCP_URL}/mcp",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    auth_token = os.getenv("MCP_AUTH_TOKEN")
    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _mcp_health() -> dict[str, Any]:
    """Check MCP server health."""
    with urllib.request.urlopen(f"{MCP_URL}/health", timeout=5) as resp:
        return json.loads(resp.read())


# ── Route mapping ────────────────────────────────────────────────────────────

ROUTES: dict[str, dict[str, Any]] = {
    # Security
    "GET /api/v1/security/scan": {
        "tool": "openclaw_security_scan",
        "defaults": {},
        "doc": "Run a security scan on the OpenClaw configuration",
    },
    # Memory
    "POST /api/v1/memory/harvest": {
        "tool": "openclaw_hebbian_harvest",
        "defaults": {},
        "doc": "Harvest session logs into Hebbian memory",
    },
    "GET /api/v1/memory/status": {
        "tool": "openclaw_hebbian_status",
        "defaults": {},
        "doc": "Get Hebbian memory dashboard (weights, drift, sessions)",
    },
    "POST /api/v1/memory/analyze": {
        "tool": "openclaw_hebbian_analyze",
        "defaults": {"since_days": 90},
        "doc": "Run Hebbian analysis on recent sessions",
    },
    "POST /api/v1/memory/weight-update": {
        "tool": "openclaw_hebbian_weight_update",
        "defaults": {"dry_run": True},
        "doc": "Compute Hebbian weight updates (dry_run by default)",
    },
    # Fleet
    "GET /api/v1/fleet/status": {
        "tool": "firm_gateway_fleet_status",
        "defaults": {},
        "doc": "Get status of all Gateway fleet instances",
    },
    # A2A
    "POST /api/v1/a2a/discover": {
        "tool": "openclaw_a2a_discovery",
        "defaults": {},
        "doc": "Discover A2A agents via Agent Cards",
    },
    "POST /api/v1/a2a/task": {
        "tool": "openclaw_a2a_task_send",
        "defaults": {},
        "doc": "Send a task to an A2A agent",
    },
    # Delivery
    "POST /api/v1/export/github-pr": {
        "tool": "firm_export_github_pr",
        "defaults": {},
        "doc": "Export a deliverable as a GitHub PR",
    },
    "POST /api/v1/export/slack": {
        "tool": "firm_export_slack_digest",
        "defaults": {},
        "doc": "Post a deliverable digest to Slack",
    },
    # Compliance
    "GET /api/v1/compliance/spec": {
        "tool": "openclaw_elicitation_audit",
        "defaults": {},
        "doc": "Run MCP spec compliance audit",
    },
}


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class FirmRESTHandler(BaseHTTPRequestHandler):
    """Simple REST handler that proxies to MCP tools."""

    def _send_json(self, status: int, data: Any) -> None:
        body = json.dumps(data, indent=2, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _route_key(self) -> str:
        path = self.path.split("?")[0]
        return f"{self.command} {path}"

    def _handle_request(self) -> None:
        # Health check
        if self.path in ("/health", "/api/v1/health"):
            try:
                mcp_health = _mcp_health()
                self._send_json(200, {"status": "ok", "mcp": mcp_health})
            except Exception as e:
                self._send_json(503, {"status": "degraded", "mcp_error": str(e)})
            return

        # API docs
        if self.path in ("/", "/api", "/api/v1"):
            docs = {
                "name": "Firm Ecosystem REST API",
                "version": "1.0.0",
                "mcp_backend": MCP_URL,
                "endpoints": {
                    route: {"tool": info["tool"], "description": info["doc"]}
                    for route, info in ROUTES.items()
                },
            }
            self._send_json(200, docs)
            return

        # Route dispatch
        key = self._route_key()
        route = ROUTES.get(key)
        if not route:
            self._send_json(404, {"error": f"Not found: {key}", "available": list(ROUTES.keys())})
            return

        try:
            body = self._read_body() if self.command in ("POST", "PUT", "PATCH") else {}
            arguments = {**route["defaults"], **body}
            start = time.perf_counter()
            result = _mcp_call(route["tool"], arguments)
            elapsed = (time.perf_counter() - start) * 1000
            self._send_json(200, {
                "tool": route["tool"],
                "result": result.get("result"),
                "elapsed_ms": round(elapsed, 1),
            })
        except Exception as e:
            self._send_json(500, {"error": str(e), "tool": route["tool"]})

    def do_GET(self) -> None:
        self._handle_request()

    def do_POST(self) -> None:
        self._handle_request()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        """Structured logging."""
        sys.stderr.write(f"[REST] {args[0]} {args[1]} {args[2]}\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Firm Ecosystem REST API wrapper")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port (default: {API_PORT})")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    args = parser.parse_args(argv)

    server = HTTPServer((args.host, args.port), FirmRESTHandler)
    print(f"Firm REST API listening on http://{args.host}:{args.port}")
    print(f"MCP backend: {MCP_URL}")
    print(f"Endpoints: {len(ROUTES)}")
    print(f"Docs: http://{args.host}:{args.port}/api/v1")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
