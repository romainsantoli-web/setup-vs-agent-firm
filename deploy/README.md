# Deployment Guide

Everything you need to deploy the Firm Ecosystem in any environment.

## Quick start (Docker Compose)

```bash
# Clone and start
git clone https://github.com/romainsantoli-web/firm-ecosystem.git
cd firm-ecosystem
docker compose up -d

# Verify
curl http://localhost:8012/health   # MCP server
curl http://localhost:8765/health   # Memory server
```

## Options

| Method | Best for | Setup time |
|--------|---------|------------|
| [Docker Compose](../docker-compose.yml) | Local dev, demos | 2 min |
| [Helm Chart](helm/) | Kubernetes production | 5 min |
| [pip install](../README.md#install) | Direct Python | 1 min |
| [Codespace](../.devcontainer/) | Zero-install browser IDE | 30 sec |

## Monitoring

1. **Prometheus**: Scrape `http://localhost:8012/metrics`
2. **Grafana**: Import [dashboard.json](grafana/dashboard.json)

```yaml
# prometheus.yml
scrape_configs:
  - job_name: firm-mcp
    static_configs:
      - targets: ["localhost:8012"]
    metrics_path: /metrics
    scrape_interval: 15s
```

## Kubernetes (Helm)

```bash
helm install firm deploy/helm/firm-ecosystem \
  --set persistence.size=5Gi \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=firm.yourdomain.com
```

See [helm/README.md](helm/README.md) for all values.

## Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   MCP Server (:8012)    │     │  Memory Server (:8765)  │
│                         │     │                         │
│  138 tools / 29 modules │◄───►│  Hebbian 4-layer system │
│  Security, A2A, Fleet   │     │  Session harvesting     │
│  Compliance, Delivery   │     │  Weight updates         │
│  /metrics (Prometheus)  │     │  Drift detection        │
└─────────────────────────┘     └─────────────────────────┘
          ▲                               ▲
          │                               │
    ┌─────┴─────┐                 ┌───────┴────────┐
    │  REST API │                 │  CLAUDE.md     │
    │  (:8080)  │                 │  (4 layers)    │
    └───────────┘                 └────────────────┘
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_EXT_HOST` | `127.0.0.1` | MCP server bind address |
| `MCP_EXT_PORT` | `8012` | MCP server port |
| `MCP_AUTH_TOKEN` | *(none)* | Bearer token for auth |
| `LOG_LEVEL` | `INFO` | Logging level |
| `TOOL_TIMEOUT_S` | `120` | Per-tool timeout (seconds) |
| `MEMORY_BACKEND` | `sqlite` | Memory storage backend |
