"""LlamaIndex integration — FirmToolSpec + FirmReader.

Connects the Firm Ecosystem MCP server to LlamaIndex's tool and reader
interfaces.

Requirements:
    pip install llama-index-core firm-sdk

Usage:
    from integrations.llamaindex_adapter import FirmToolSpec, FirmReader

    # As tools (for agents)
    tools = FirmToolSpec().to_tool_list()

    # As a reader (for indexing)
    reader = FirmReader()
    docs = reader.load_data(query="security patterns")

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, List, Optional


# ── MCP Client Helper ────────────────────────────────────────────────────────

class _MCPClient:
    """Lightweight MCP client shared by adapters."""

    def __init__(self, mcp_url: str = "http://127.0.0.1:8012", auth_token: str | None = None):
        self.mcp_url = mcp_url
        self.auth_token = auth_token
        self._rpc_id = 0

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        self._rpc_id += 1
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": self._rpc_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }).encode()
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        req = urllib.request.Request(
            f"{self.mcp_url}/mcp", data=payload, headers=headers,
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result.get("result", result)

    def list_tools(self) -> list[dict]:
        self._rpc_id += 1
        payload = json.dumps({
            "jsonrpc": "2.0", "id": self._rpc_id,
            "method": "tools/list", "params": {},
        }).encode()
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        req = urllib.request.Request(
            f"{self.mcp_url}/mcp", data=payload, headers=headers,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        return result.get("result", {}).get("tools", [])


# ── Tool Spec ────────────────────────────────────────────────────────────────

try:
    from llama_index.core.tools import FunctionTool, ToolMetadata

    class FirmToolSpec:
        """LlamaIndex ToolSpec wrapping Firm MCP tools.

        Usage:
            spec = FirmToolSpec()
            tools = spec.to_tool_list()
            # Use in agent: agent = ReActAgent.from_tools(tools, llm=llm)
        """

        def __init__(
            self,
            mcp_url: str = "http://127.0.0.1:8012",
            auth_token: str | None = None,
            tools_filter: list[str] | None = None,
        ):
            self._client = _MCPClient(mcp_url, auth_token)
            self.tools_filter = tools_filter

        def to_tool_list(self) -> List[FunctionTool]:
            mcp_tools = self._client.list_tools()
            tools = []
            for t in mcp_tools:
                name = t["name"]
                if self.tools_filter and name not in self.tools_filter:
                    continue
                desc = t.get("description", name)[:500]
                tool_name = name

                def make_fn(tn: str):
                    def fn(**kwargs: Any) -> str:
                        result = self._client.call_tool(tn, kwargs)
                        return json.dumps(result, indent=2)
                    fn.__name__ = tn
                    fn.__doc__ = desc
                    return fn

                tools.append(FunctionTool.from_defaults(
                    fn=make_fn(tool_name),
                    tool_metadata=ToolMetadata(name=tool_name, description=desc),
                ))
            return tools

except ImportError:
    class FirmToolSpec:  # type: ignore[no-redef]
        """Stub: install llama-index-core for full functionality."""
        def __init__(self, **kwargs: Any):
            raise ImportError("FirmToolSpec requires: pip install llama-index-core")


# ── Reader ───────────────────────────────────────────────────────────────────

try:
    from llama_index.core.readers.base import BaseReader
    from llama_index.core.schema import Document

    class FirmReader(BaseReader):
        """LlamaIndex reader that loads Firm Hebbian memory data as Documents.

        Usage:
            reader = FirmReader()
            docs = reader.load_data(query="security patterns")
        """

        def __init__(
            self,
            mcp_url: str = "http://127.0.0.1:8012",
            auth_token: str | None = None,
        ):
            super().__init__()
            self._client = _MCPClient(mcp_url, auth_token)

        def load_data(self, query: str = "", **kwargs: Any) -> List[Document]:
            """Load memory data as LlamaIndex Documents."""
            try:
                result = self._client.call_tool("openclaw_hebbian_status", {})
                data = result if isinstance(result, dict) else {}
                content_items = data.get("content", [])
                if isinstance(content_items, list) and content_items:
                    if isinstance(content_items[0], dict) and "text" in content_items[0]:
                        content_items = [c["text"] for c in content_items]
                elif not content_items:
                    content_items = [json.dumps(data)]
            except Exception:
                return []

            docs = []
            query_lower = query.lower()
            for item in content_items:
                text = str(item)
                if not query or query_lower in text.lower():
                    docs.append(Document(
                        text=text,
                        metadata={"source": "firm_hebbian_memory"},
                    ))
            return docs

except ImportError:
    class FirmReader:  # type: ignore[no-redef]
        """Stub: install llama-index-core for full functionality."""
        def __init__(self, **kwargs: Any):
            raise ImportError("FirmReader requires: pip install llama-index-core")
