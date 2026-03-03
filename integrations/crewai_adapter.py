"""CrewAI adapter — use Firm Ecosystem tools as CrewAI tools.

Wraps MCP tools as CrewAI-compatible `Tool` objects, enabling
direct use in CrewAI agent pipelines.

Usage:
    from integrations.crewai_adapter import FirmCrewTools

    firm_tools = FirmCrewTools()
    tools = firm_tools.get_tools()  # list of crewai Tool objects

    # Use in a CrewAI agent
    from crewai import Agent
    agent = Agent(
        role="Security Auditor",
        goal="Audit the AI agent configuration",
        tools=tools,
    )

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

MCP_URL = os.getenv("FIRM_MCP_URL", "http://127.0.0.1:8012")

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
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _list_tools() -> list[dict[str, Any]]:
    """List available MCP tools."""
    global _rpc_id
    _rpc_id += 1
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": _rpc_id,
        "method": "tools/list",
        "params": {},
    }).encode()
    req = urllib.request.Request(
        f"{MCP_URL}/mcp",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("result", {}).get("tools", [])


# ── CrewAI Adapter ───────────────────────────────────────────────────────────


class FirmCrewTools:
    """Adapter that wraps Firm MCP tools as CrewAI Tool objects.

    Example:
        >>> firm = FirmCrewTools()
        >>> tools = firm.get_tools()
        >>> len(tools)  # one Tool per MCP tool
        138

        # Filter by category
        >>> security_tools = firm.get_tools(filter_prefix="openclaw_security")
    """

    def __init__(self, mcp_url: str | None = None):
        self._mcp_url = mcp_url or MCP_URL
        self._tools_cache: list[dict] | None = None

    def _fetch_tools(self) -> list[dict[str, Any]]:
        if self._tools_cache is None:
            self._tools_cache = _list_tools()
        return self._tools_cache

    def get_tools(self, filter_prefix: str = "") -> list:
        """Return a list of CrewAI Tool objects wrapping MCP tools.

        Args:
            filter_prefix: Only include tools whose name starts with this prefix.

        Returns:
            List of crewai.tools.Tool objects.
        """
        try:
            from crewai.tools import Tool
        except ImportError:
            raise ImportError(
                "CrewAI adapter requires: pip install crewai\n"
                "See https://docs.crewai.com for installation."
            )

        mcp_tools = self._fetch_tools()
        crew_tools = []

        for t in mcp_tools:
            name = t.get("name", "")
            if filter_prefix and not name.startswith(filter_prefix):
                continue

            description = t.get("description", name)
            input_schema = t.get("inputSchema", {})

            def _make_func(tool_name: str):
                def func(**kwargs: Any) -> str:
                    result = _mcp_call(tool_name, kwargs)
                    return json.dumps(result.get("result", result), indent=2)
                func.__name__ = tool_name
                func.__doc__ = description
                return func

            crew_tools.append(Tool(
                name=name,
                description=description[:500],  # CrewAI has a description length limit
                func=_make_func(name),
            ))

        return crew_tools

    def get_security_tools(self) -> list:
        """Get only security and audit tools."""
        return self.get_tools(filter_prefix="openclaw_security") + \
               self.get_tools(filter_prefix="openclaw_sandbox")

    def get_memory_tools(self) -> list:
        """Get only Hebbian memory tools."""
        return self.get_tools(filter_prefix="openclaw_hebbian")

    def get_a2a_tools(self) -> list:
        """Get only A2A protocol tools."""
        return self.get_tools(filter_prefix="openclaw_a2a")


# ── Standalone usage ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    firm = FirmCrewTools()
    try:
        tools = firm.get_tools()
        print(f"Loaded {len(tools)} CrewAI tools from {MCP_URL}")
        for t in tools[:5]:
            print(f"  - {t.name}: {t.description[:80]}...")
    except ImportError as e:
        print(f"CrewAI not installed: {e}")
    except Exception as e:
        print(f"MCP server not reachable: {e}")
