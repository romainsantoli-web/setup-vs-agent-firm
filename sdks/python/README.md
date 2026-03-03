# firm-sdk (Python)

Typed Python client for the Firm Ecosystem MCP server.

## Install

```bash
pip install firm-sdk
# For async support:
pip install firm-sdk[async]
```

## Quick start

```python
from firm_sdk import FirmClient

client = FirmClient()  # localhost:8012

# Health check
health = client.health()

# Security scan
result = client.security_scan(config_path="/etc/openclaw/config.yaml")
print(result.ok, result.data)

# Memory status
status = client.memory_status()

# Call any tool by name
result = client.call_tool("openclaw_hebbian_analyze", {"since_days": 30})
```

## Async

```python
import asyncio
from firm_sdk import FirmAsyncClient

async def main():
    async with FirmAsyncClient() as client:
        health = await client.health()
        result = await client.memory_status()
        print(result.data)

asyncio.run(main())
```

## Configuration

```python
client = FirmClient(
    base_url="http://mcp.example.com:8012",
    auth_token="your-token",
    timeout=60.0,
)
```

## Available methods

| Method | MCP Tool | Description |
|--------|----------|-------------|
| `security_scan()` | `openclaw_security_scan` | Run security audit |
| `memory_status()` | `openclaw_hebbian_status` | Hebbian memory dashboard |
| `memory_analyze()` | `openclaw_hebbian_analyze` | Run Hebbian analysis |
| `memory_weight_update()` | `openclaw_hebbian_weight_update` | Update weights |
| `fleet_status()` | `firm_gateway_fleet_status` | Fleet status |
| `a2a_discover()` | `openclaw_a2a_discovery` | Discover A2A agents |
| `export_github_pr()` | `firm_export_github_pr` | Export as GitHub PR |
| `export_slack()` | `firm_export_slack_digest` | Post to Slack |
| `compliance_check()` | `openclaw_elicitation_audit` | Spec compliance |
| `call_tool(name, args)` | Any tool | Generic tool call |
