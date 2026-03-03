# firm-sdk (TypeScript)

Typed TypeScript client for the Firm Ecosystem MCP server.

## Install

```bash
npm install firm-sdk
```

## Quick start

```ts
import { FirmClient } from "firm-sdk";

const client = new FirmClient(); // localhost:8012

// Health check
const health = await client.health();

// Security scan
const result = await client.securityScan("/etc/openclaw/config.yaml");
console.log(result.ok, result.data);

// Memory status
const status = await client.memoryStatus();

// Generic tool call
const r = await client.callTool("openclaw_hebbian_analyze", { since_days: 30 });
```

## Configuration

```ts
const client = new FirmClient({
  baseUrl: "http://mcp.example.com:8012",
  authToken: "your-token",
  timeout: 60_000,
});
```

## Available methods

| Method | MCP Tool | Description |
|--------|----------|-------------|
| `securityScan()` | `openclaw_security_scan` | Run security audit |
| `memoryStatus()` | `openclaw_hebbian_status` | Memory dashboard |
| `memoryAnalyze()` | `openclaw_hebbian_analyze` | Run analysis |
| `memoryWeightUpdate()` | `openclaw_hebbian_weight_update` | Update weights |
| `fleetStatus()` | `firm_gateway_fleet_status` | Fleet status |
| `a2aDiscover()` | `openclaw_a2a_discovery` | Discover agents |
| `exportGithubPr()` | `firm_export_github_pr` | Export as PR |
| `exportSlack()` | `firm_export_slack_digest` | Post to Slack |
| `callTool(name, args)` | Any tool | Generic call |
