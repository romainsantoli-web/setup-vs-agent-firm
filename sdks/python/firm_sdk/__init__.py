"""firm-sdk — Python client for the Firm Ecosystem MCP server.

Provides a typed, async-capable client for calling MCP tools
without needing to know the JSON-RPC protocol.

Usage:
    from firm_sdk import FirmClient

    client = FirmClient()  # defaults to localhost:8012
    result = client.security_scan(config_path="/etc/openclaw/config.yaml")

    # Async usage
    async with FirmAsyncClient() as client:
        status = await client.memory_status()

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Result from an MCP tool call."""
    tool: str
    ok: bool
    data: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0


@dataclass
class FirmClient:
    """Synchronous Python client for the Firm MCP server.

    Examples:
        >>> client = FirmClient()
        >>> client.health()
        {'status': 'ok', 'tools': 138, ...}

        >>> result = client.call_tool("openclaw_hebbian_status", {})
        >>> result.ok
        True
    """
    base_url: str = "http://127.0.0.1:8012"
    auth_token: str | None = None
    timeout: float = 120.0
    _rpc_id: int = field(default=0, repr=False)

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.auth_token:
            h["Authorization"] = f"Bearer {self.auth_token}"
        return h

    def _next_id(self) -> int:
        self._rpc_id += 1
        return self._rpc_id

    def health(self) -> dict[str, Any]:
        """Check server health."""
        req = urllib.request.Request(f"{self.base_url}/health", headers=self._headers())
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())

    def list_tools(self) -> list[dict[str, Any]]:
        """List all available MCP tools."""
        return self._rpc("tools/list", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
        """Call an MCP tool by name.

        Args:
            name: Tool name (e.g. "openclaw_security_scan")
            arguments: Tool arguments dict

        Returns:
            ToolResult with ok=True on success
        """
        import time
        start = time.perf_counter()
        try:
            result = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
            elapsed = (time.perf_counter() - start) * 1000
            if "error" in result:
                return ToolResult(tool=name, ok=False, error=str(result["error"]), elapsed_ms=elapsed)
            return ToolResult(tool=name, ok=True, data=result.get("result"), elapsed_ms=elapsed)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(tool=name, ok=False, error=str(e), elapsed_ms=elapsed)

    def _rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/mcp",
            data=payload,
            headers=self._headers(),
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())

    # ── Convenience methods ──────────────────────────────────────────────

    def security_scan(self, config_path: str = "", **kwargs: Any) -> ToolResult:
        """Run a security scan."""
        return self.call_tool("openclaw_security_scan", {"config_path": config_path, **kwargs})

    def memory_status(self) -> ToolResult:
        """Get Hebbian memory status."""
        return self.call_tool("openclaw_hebbian_status", {})

    def memory_analyze(self, since_days: int = 90) -> ToolResult:
        """Run Hebbian memory analysis."""
        return self.call_tool("openclaw_hebbian_analyze", {"since_days": since_days})

    def memory_weight_update(self, dry_run: bool = True) -> ToolResult:
        """Compute Hebbian weight updates."""
        return self.call_tool("openclaw_hebbian_weight_update", {"dry_run": dry_run})

    def fleet_status(self) -> ToolResult:
        """Get fleet status."""
        return self.call_tool("firm_gateway_fleet_status", {})

    def a2a_discover(self, url: str = "", **kwargs: Any) -> ToolResult:
        """Discover A2A agents."""
        return self.call_tool("openclaw_a2a_discovery", {"url": url, **kwargs})

    def export_github_pr(self, **kwargs: Any) -> ToolResult:
        """Export deliverable as GitHub PR."""
        return self.call_tool("firm_export_github_pr", kwargs)

    def export_slack(self, **kwargs: Any) -> ToolResult:
        """Post digest to Slack."""
        return self.call_tool("firm_export_slack_digest", kwargs)

    def compliance_check(self, config_path: str = "", **kwargs: Any) -> ToolResult:
        """Run spec compliance check."""
        return self.call_tool("openclaw_elicitation_audit", {"config_path": config_path, **kwargs})


# ── Async client ─────────────────────────────────────────────────────────────

class FirmAsyncClient:
    """Async Python client for the Firm MCP server.

    Usage:
        async with FirmAsyncClient() as client:
            health = await client.health()
            result = await client.call_tool("openclaw_hebbian_status", {})
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8012",
        auth_token: str | None = None,
        timeout: float = 120.0,
    ):
        self.base_url = base_url
        self.auth_token = auth_token
        self.timeout = timeout
        self._rpc_id = 0
        self._session = None

    async def __aenter__(self):
        try:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        except ImportError:
            raise ImportError("Async client requires: pip install aiohttp")
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.auth_token:
            h["Authorization"] = f"Bearer {self.auth_token}"
        return h

    def _next_id(self) -> int:
        self._rpc_id += 1
        return self._rpc_id

    async def health(self) -> dict[str, Any]:
        """Check server health."""
        async with self._session.get(f"{self.base_url}/health") as resp:
            return await resp.json()

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available MCP tools."""
        result = await self._rpc("tools/list", {})
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
        """Call an MCP tool by name."""
        import time
        start = time.perf_counter()
        try:
            result = await self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
            elapsed = (time.perf_counter() - start) * 1000
            if "error" in result:
                return ToolResult(tool=name, ok=False, error=str(result["error"]), elapsed_ms=elapsed)
            return ToolResult(tool=name, ok=True, data=result.get("result"), elapsed_ms=elapsed)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(tool=name, ok=False, error=str(e), elapsed_ms=elapsed)

    async def _rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }
        async with self._session.post(f"{self.base_url}/mcp", json=payload) as resp:
            return await resp.json()

    # ── Convenience methods ──────────────────────────────────────────────

    async def security_scan(self, config_path: str = "", **kw: Any) -> ToolResult:
        return await self.call_tool("openclaw_security_scan", {"config_path": config_path, **kw})

    async def memory_status(self) -> ToolResult:
        return await self.call_tool("openclaw_hebbian_status", {})

    async def memory_analyze(self, since_days: int = 90) -> ToolResult:
        return await self.call_tool("openclaw_hebbian_analyze", {"since_days": since_days})

    async def fleet_status(self) -> ToolResult:
        return await self.call_tool("firm_gateway_fleet_status", {})
