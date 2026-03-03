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

## CrewAI

```python
from integrations.crewai_adapter import FirmCrewTools

firm = FirmCrewTools()
tools = firm.get_tools()  # all 138 MCP tools as CrewAI Tools

# Filter by category
security_tools = firm.get_security_tools()
memory_tools = firm.get_memory_tools()

# Use in a CrewAI agent
from crewai import Agent
agent = Agent(role="Auditor", tools=tools)
```

Requires: `pip install crewai`

## AutoGen

```python
from integrations.autogen_adapter import FirmAutoGenTools

firm = FirmAutoGenTools()

# Get OpenAI-compatible tool schemas for llm_config
schemas = firm.get_tool_schemas()

# Get function_map for UserProxyAgent
func_map = firm.get_function_map()

# Use with AutoGen
from autogen import AssistantAgent, UserProxyAgent
assistant = AssistantAgent("auditor", llm_config={"tools": schemas})
user_proxy = UserProxyAgent("user", function_map=func_map)
```

Requires: `pip install pyautogen`
