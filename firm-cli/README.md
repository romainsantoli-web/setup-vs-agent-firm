# firm-cli

> One command to create, start, and manage AI agent firms with inter-session Hebbian memory.

[![PyPI](https://img.shields.io/pypi/v/firm-cli)](https://pypi.org/project/firm-cli/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

## Install

```bash
pip install firm-cli
```

## Quick start

```bash
# Generate a fintech startup firm
firm init --sector fintech --size startup --output ./my-firm

# Start both MCP servers (138 + 18 tools)
cd my-firm && firm start

# Check status
firm status

# View Hebbian memory dashboard
firm memory status
```

## What it does

`firm init` generates a complete **VS Code Copilot agent firm** — a pyramidal organization of AI agents (CEO → Departments → Specialists) pre-configured for your industry sector.

| Size | Departments | Agents |
|------|------------|--------|
| startup | 4 | ~20 |
| scaleup | 12 | ~60 |
| enterprise | 18 | ~100+ |

**15 sectors**: generic, legal, medtech, ecommerce, fintech, saas, manufacturing, education, realestate, logistics, media, automotive, energy, hr, consulting

**7 stacks**: typescript, python, java, dotnet, go, rust, mixed

## Commands

| Command | Description |
|---------|-------------|
| `firm init` | Generate a new AI agent firm |
| `firm start` | Start MCP servers (openclaw-extensions + memory) |
| `firm stop` | Stop MCP servers |
| `firm status` | Show ecosystem component status |
| `firm memory status` | Hebbian memory dashboard (weights, drift) |
| `firm memory analyze` | Run Hebbian clustering analysis |
| `firm config set <k> <v>` | Set configuration |
| `firm config show` | Show current configuration |

## Part of the Firm Ecosystem

- **[firm-ecosystem](https://github.com/romainsantoli-web/firm-ecosystem)** — Architecture docs
- **[mcp-openclaw-extensions](https://github.com/romainsantoli-web/mcp-openclaw)** — 138 MCP tools
- **[Memory-os-ai](https://github.com/romainsantoli-web/Memory-os-ai)** — Semantic memory engine

## License

MIT
