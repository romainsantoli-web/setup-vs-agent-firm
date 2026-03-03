# Memory-os-ai — Standalone Hebbian Memory for AI Agents

> **The first open-source inter-session memory system for AI agents,
> inspired by neuroscience's Hebbian learning rule.**

[![PyPI](https://img.shields.io/pypi/v/memory-os-ai)](https://pypi.org/project/memory-os-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/romainsantoli-web/Memory-os-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/romainsantoli-web/Memory-os-ai/actions)

---

## What is Memory-os-ai?

Memory-os-ai gives your AI agents **persistent, adaptive memory** that strengthens
over time — just like biological neurons. Instead of losing context between sessions,
your agents remember what matters and forget what doesn't.

**Key insight:** Neurons that fire together, wire together. Memory-os-ai applies
this principle to AI agent interactions, creating a 4-layer memory architecture
that continuously learns from usage patterns.

### 4-Layer Hebbian Architecture

| Layer | Purpose | Decay Rate |
|-------|---------|------------|
| **L1 — Working** | Current session context | Fast (τ=0.1) |
| **L2 — Episodic** | Recent sessions & interactions | Medium (τ=0.05) |
| **L3 — Semantic** | Extracted rules & patterns | Slow (τ=0.01) |
| **L4 — Procedural** | Proven workflows & best practices | Minimal (τ=0.001) |

**Weight update formula:**
```
w_new = w_old + η × activation - λ × (1 - activation)
```

---

## Quick Start

### Install

```bash
pip install memory-os-ai
```

### Use as a library

```python
from memory_os_ai import HebbianMemory

memory = HebbianMemory()

# Store a learning
memory.store("always-test", {
    "rule": "Always run tests before pushing",
    "layer": "L3",
    "weight": 0.85,
})

# Search for relevant memories
results = memory.search("testing best practices", limit=5)
for r in results:
    print(f"  {r.key}: weight={r.weight:.2f}")

# Hebbian update — strengthen co-activated memories
memory.hebbian_update(["always-test", "use-ci"], activation=1.0)
```

### Use as an MCP server

```bash
# Start the SSE server
memory-os-ai --sse --port 8765

# Or with Streamable HTTP
memory-os-ai --streamable-http --port 8765
```

Add to your MCP client config:
```json
{
  "mcpServers": {
    "memory-os-ai": {
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

### Use with firm-cli (recommended)

For the full ecosystem experience with 138+ MCP tools:

```bash
pip install firm-cli
firm init --sector saas --size startup
firm start   # starts memory-os-ai + mcp-openclaw-extensions
```

See the [firm-ecosystem](https://github.com/romainsantoli-web/firm-ecosystem)
for the complete platform.

---

## Embedding Models

Memory-os-ai supports configurable embedding models via `sentence-transformers`:

| Model | Languages | Best For |
|-------|-----------|----------|
| `all-MiniLM-L6-v2` (default) | English | Fast, general purpose |
| `paraphrase-multilingual-MiniLM-L12-v2` | 50+ (incl. French) | Multilingual teams |
| `BAAI/bge-m3` | 100+ | Maximum quality |
| `dangvantuan/sentence-camembert-large` | French | French-specific |

Configure:
```bash
firm config set memory.model paraphrase-multilingual-MiniLM-L12-v2
```

---

## Storage Backends

| Backend | Install | Best For |
|---------|---------|----------|
| SQLite (default) | Built-in | Local, single-agent |
| Redis | `pip install redis` | Distributed |
| PostgreSQL + pgvector | `pip install psycopg2-binary` | Production |
| ChromaDB | `pip install chromadb` | Vector similarity |

---

## API Reference

### Core Methods

| Method | Description |
|--------|-------------|
| `store(key, data, metadata?)` | Store or update a memory record |
| `get(key)` | Retrieve a single memory |
| `search(query, limit=10)` | Semantic search across memories |
| `delete(key)` | Remove a memory |
| `hebbian_update(keys, activation)` | Strengthen co-activated memories |
| `decay(factor?)` | Apply time-based decay to all memories |
| `export_json(path)` | Export all memories to JSON |
| `import_json(path, merge?)` | Import memories from JSON |

### MCP Tools (when running as server)

| Tool | Description |
|------|-------------|
| `memory_store` | Store a new memory |
| `memory_search` | Semantic search |
| `memory_analyze` | Run Hebbian analysis |
| `memory_status` | Dashboard with stats |
| `memory_export` | Export to JSON |
| `memory_import` | Import from JSON |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Memory-os-ai                   │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ L1 Work  │→ │ L2 Episo │→ │ L3 Seman │→ │ L4 Proced │
│  │ τ=0.1    │  │ τ=0.05   │  │ τ=0.01   │  │ τ=0.001   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│         ↑               ↑               ↑
│     Hebbian          Weight           Drift
│     Harvest          Update          Check
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │  Backend: SQLite│Redis│Postgres│Chroma│  │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐   │
│  │ MCP SSE │  │ REST API │  │ Python   │   │
│  │  :8765  │  │  :8766   │  │ Library  │   │
│  └─────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/romainsantoli-web/Memory-os-ai.git
cd Memory-os-ai
pip install -e ".[dev]"
pytest -v  # 348 tests
```

---

## Part of the Firm Ecosystem

Memory-os-ai is the memory engine of the **[firm-ecosystem](https://github.com/romainsantoli-web/firm-ecosystem)** —
a complete platform for building AI agent teams with inter-session Hebbian memory.

| Component | Description |
|-----------|-------------|
| [firm-cli](https://pypi.org/project/firm-cli/) | CLI to create & manage agent firms |
| [firm-ecosystem](https://github.com/romainsantoli-web/firm-ecosystem) | Full platform + integrations |
| [mcp-openclaw-extensions](https://github.com/romainsantoli-web/mcp-openclaw-extensions) | 138 MCP tools for security, compliance, orchestration |

---

## License

MIT — see [LICENSE](LICENSE).

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
