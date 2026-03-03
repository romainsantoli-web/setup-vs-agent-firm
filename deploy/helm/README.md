# Helm Chart — Firm Ecosystem

Deploy the Firm Ecosystem to Kubernetes with one command.

## Quick start

```bash
helm install firm deploy/helm/firm-ecosystem
```

## Custom values

```bash
helm install firm deploy/helm/firm-ecosystem \
  --set mcpServer.replicaCount=2 \
  --set memoryServer.enabled=true \
  --set persistence.size=5Gi \
  --set ingress.enabled=true
```

## Components

| Component | Default Port | Description |
|-----------|-------------|-------------|
| MCP Server | 8012 | 138 MCP tools (security, memory, A2A, compliance) |
| Memory Server | 8765 | Hebbian memory with 4-layer CLAUDE.md system |

## Configuration

See [values.yaml](firm-ecosystem/values.yaml) for all options.

Key settings:
- `mcpServer.env.MCP_AUTH_TOKEN` — Bearer auth token
- `persistence.size` — Storage for memory data
- `ingress.enabled` — Enable Ingress for external access
