# Grafana Dashboard

Pre-built dashboard for monitoring the Firm Ecosystem MCP server.

## Import

1. Open Grafana → Dashboards → Import
2. Upload `dashboard.json` or paste its contents
3. Select your Prometheus data source
4. Click Import

## Prerequisites

- Prometheus scraping the MCP `/metrics` endpoint
- MCP server running with metrics enabled (default on port 8012)

### Prometheus config

```yaml
scrape_configs:
  - job_name: "firm-mcp"
    scrape_interval: 15s
    static_configs:
      - targets: ["localhost:8012"]
    metrics_path: "/metrics"
```

## Panels

### Overview row
- Total Requests, Tool Errors, Tool Calls, Timeouts, Auth Failures, Uptime

### Tool Performance row
- Top 15 Tools by Call Count
- Tool Latency (average ms)
- Tool Errors by Tool
- Request Rate (5m rolling avg)

### Memory row
- Hebbian Memory tool calls
- Security Audit tool calls
- A2A Bridge tool calls

## Alerts (suggested)

| Alert | Condition | Severity |
|-------|-----------|----------|
| High error rate | `mcp_tool_errors_total / mcp_tool_calls_total > 0.05` | warning |
| Auth failures | `mcp_auth_failures_total > 0` | critical |
| Tool timeout spike | `rate(mcp_tool_timeouts_total[5m]) > 1` | warning |
