"""AutoGen adapter — use Firm Ecosystem tools in Microsoft AutoGen agents.

Wraps MCP tools as AutoGen-compatible `FunctionTool` objects, enabling
direct use in AutoGen multi-agent conversations.

Usage:
    from integrations.autogen_adapter import FirmAutoGenTools

    firm = FirmAutoGenTools()
    tools = firm.get_tools()

    # Use in AutoGen AssistantAgent
    from autogen import AssistantAgent
    agent = AssistantAgent(
        name="security_auditor",
        llm_config={"tools": [t.schema for t in tools]},
    )

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

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
    """List available MCP tools from the server."""
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


# ── AutoGen Tool Wrapper ─────────────────────────────────────────────────────


@dataclass
class FirmTool:
    """A Firm MCP tool wrapped for AutoGen compatibility.

    Provides both the callable function and the JSON Schema needed
    by AutoGen's function calling mechanism.
    """
    name: str
    description: str
    func: Callable[..., str]
    parameters: dict[str, Any] = field(default_factory=dict)

    @property
    def schema(self) -> dict[str, Any]:
        """Return the OpenAI function-calling compatible schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description[:1024],
                "parameters": self.parameters or {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }

    def __call__(self, **kwargs: Any) -> str:
        return self.func(**kwargs)


class FirmAutoGenTools:
    """Adapter that wraps Firm MCP tools for use in AutoGen agents.

    Example:
        >>> firm = FirmAutoGenTools()
        >>> tools = firm.get_tools()
        >>> tools[0].schema
        {'type': 'function', 'function': {'name': '...', ...}}

        # Register with AutoGen
        >>> for tool in tools:
        ...     agent.register_function({tool.name: tool.func})
    """

    def __init__(self, mcp_url: str | None = None):
        self._mcp_url = mcp_url or MCP_URL
        self._tools_cache: list[dict] | None = None

    def _fetch_tools(self) -> list[dict[str, Any]]:
        if self._tools_cache is None:
            self._tools_cache = _list_tools()
        return self._tools_cache

    def get_tools(self, filter_prefix: str = "") -> list[FirmTool]:
        """Return a list of FirmTool objects wrapping MCP tools.

        Args:
            filter_prefix: Only include tools whose name starts with this prefix.

        Returns:
            List of FirmTool objects with .schema and .func callable.
        """
        mcp_tools = self._fetch_tools()
        tools = []

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

            tools.append(FirmTool(
                name=name,
                description=description,
                func=_make_func(name),
                parameters=input_schema,
            ))

        return tools

    def get_function_map(self, filter_prefix: str = "") -> dict[str, Callable]:
        """Return a name→callable mapping for AutoGen's function_map.

        Usage with AutoGen:
            agent = UserProxyAgent(
                function_map=firm.get_function_map()
            )
        """
        return {t.name: t.func for t in self.get_tools(filter_prefix)}

    def get_tool_schemas(self, filter_prefix: str = "") -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for llm_config.

        Usage with AutoGen:
            assistant = AssistantAgent(
                llm_config={"tools": firm.get_tool_schemas()}
            )
        """
        return [t.schema for t in self.get_tools(filter_prefix)]

    def get_security_tools(self) -> list[FirmTool]:
        """Get only security and audit tools."""
        return self.get_tools(filter_prefix="openclaw_security") + \
               self.get_tools(filter_prefix="openclaw_sandbox")

    def get_memory_tools(self) -> list[FirmTool]:
        """Get only Hebbian memory tools."""
        return self.get_tools(filter_prefix="openclaw_hebbian")

    def get_a2a_tools(self) -> list[FirmTool]:
        """Get only A2A protocol tools."""
        return self.get_tools(filter_prefix="openclaw_a2a")


# ── Standalone usage ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    firm = FirmAutoGenTools()
    try:
        tools = firm.get_tools()
        print(f"Loaded {len(tools)} AutoGen tools from {MCP_URL}")
        for t in tools[:5]:
            print(f"  - {t.name}: {t.description[:80]}...")
            print(f"    Schema keys: {list(t.schema['function'].keys())}")
    except Exception as e:
        print(f"Failed: {e}")
