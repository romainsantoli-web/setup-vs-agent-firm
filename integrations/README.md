# Integrations

Adapters and wrappers connecting Firm Ecosystem to external tools and frameworks.

## REST API

HTTP wrapper for MCP tools — no MCP knowledge required.

```bash
python -m integrations.rest_api           # Start on :8080
curl http://localhost:8080/api/v1/health   # Health check
curl http://localhost:8080/api/v1/memory/status  # Memory status
curl -X POST http://localhost:8080/api/v1/memory/analyze  # Run analysis
```

See [rest_api.py](rest_api.py) for all endpoints.

## LangChain

```python
from integrations.langchain_adapter import FirmMemoryRetriever
retriever = FirmMemoryRetriever(mcp_url="http://localhost:8012")
docs = retriever.get_relevant_documents("authentication patterns")
```

## LlamaIndex

```python
from integrations.llamaindex_adapter import FirmToolSpec
tools = FirmToolSpec(mcp_url="http://localhost:8012").to_tool_list()
```
