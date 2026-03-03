"""LangChain integration — FirmMemoryRetriever + FirmToolkit.

Connects the Firm Ecosystem MCP server to LangChain's retriever
and tool interfaces.

Requirements:
    pip install langchain-core firm-sdk

Usage:
    from integrations.langchain_adapter import FirmMemoryRetriever, FirmToolkit

    # As a retriever (for RAG chains)
    retriever = FirmMemoryRetriever(mcp_url="http://localhost:8012")
    docs = retriever.invoke("authentication patterns")

    # As tools (for agents)
    toolkit = FirmToolkit(mcp_url="http://localhost:8012")
    tools = toolkit.get_tools()

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, List, Optional


# ── Retriever ────────────────────────────────────────────────────────────────

try:
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever

    class FirmMemoryRetriever(BaseRetriever):
        """LangChain retriever backed by the Firm Hebbian memory.

        Queries the MCP server for memory patterns matching the query,
        returning them as LangChain Document objects.
        """

        mcp_url: str = "http://127.0.0.1:8012"
        auth_token: Optional[str] = None
        top_k: int = 10

        def _get_relevant_documents(
            self,
            query: str,
            *,
            run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        ) -> List[Document]:
            """Retrieve memory patterns matching the query."""
            try:
                result = self._call_tool("openclaw_hebbian_status", {})
                data = result.get("result", {})
                if isinstance(data, list):
                    content_items = data
                elif isinstance(data, dict):
                    content_items = data.get("content", [])
                    if isinstance(content_items, list) and content_items:
                        if isinstance(content_items[0], dict) and "text" in content_items[0]:
                            content_items = [c["text"] for c in content_items]
                else:
                    content_items = [str(data)]
            except Exception:
                return []

            # Filter by query relevance (simple keyword matching)
            query_lower = query.lower()
            docs = []
            for item in content_items:
                text = str(item)
                if query_lower in text.lower() or not query.strip():
                    docs.append(Document(
                        page_content=text,
                        metadata={"source": "firm_hebbian_memory", "mcp_url": self.mcp_url},
                    ))
                if len(docs) >= self.top_k:
                    break

            return docs

        def _call_tool(self, name: str, arguments: dict) -> dict:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }).encode()
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            req = urllib.request.Request(
                f"{self.mcp_url}/mcp", data=payload, headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())

except ImportError:
    # LangChain not installed — provide a stub
    class FirmMemoryRetriever:  # type: ignore[no-redef]
        """Stub: install langchain-core for full functionality."""
        def __init__(self, **kwargs: Any):
            raise ImportError("FirmMemoryRetriever requires: pip install langchain-core")


# ── Toolkit (Tools for Agents) ───────────────────────────────────────────────

try:
    from langchain_core.tools import StructuredTool

    class FirmToolkit:
        """Exposes Firm MCP tools as LangChain StructuredTool instances.

        Usage:
            toolkit = FirmToolkit()
            tools = toolkit.get_tools()
            # Use in an agent: agent = create_tool_calling_agent(llm, tools, prompt)
        """

        def __init__(
            self,
            mcp_url: str = "http://127.0.0.1:8012",
            auth_token: str | None = None,
            tools_filter: list[str] | None = None,
        ):
            self.mcp_url = mcp_url
            self.auth_token = auth_token
            self.tools_filter = tools_filter

        def _call_tool(self, name: str, **kwargs: Any) -> str:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": name, "arguments": kwargs},
            }).encode()
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            req = urllib.request.Request(
                f"{self.mcp_url}/mcp", data=payload, headers=headers,
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            return json.dumps(result.get("result", result), indent=2)

        def _list_mcp_tools(self) -> list[dict]:
            payload = json.dumps({
                "jsonrpc": "2.0", "id": 1,
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

        def get_tools(self) -> list[StructuredTool]:
            """Get LangChain tools wrapping MCP tools."""
            mcp_tools = self._list_mcp_tools()
            lc_tools = []
            for t in mcp_tools:
                name = t["name"]
                if self.tools_filter and name not in self.tools_filter:
                    continue
                desc = t.get("description", name)[:500]
                tool_name = name  # capture for closure

                def make_fn(tn: str):
                    def fn(**kwargs: Any) -> str:
                        return self._call_tool(tn, **kwargs)
                    fn.__name__ = tn
                    fn.__doc__ = desc
                    return fn

                lc_tools.append(StructuredTool.from_function(
                    func=make_fn(tool_name),
                    name=tool_name,
                    description=desc,
                ))
            return lc_tools

except ImportError:
    class FirmToolkit:  # type: ignore[no-redef]
        """Stub: install langchain-core for full functionality."""
        def __init__(self, **kwargs: Any):
            raise ImportError("FirmToolkit requires: pip install langchain-core")
