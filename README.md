<div align="center">

# 🧠 Firm Ecosystem

**The inter-session memory layer for AI agents.**

Your AI agents forget everything between sessions. Firm fixes that.

[![PyPI — firm-cli](https://img.shields.io/pypi/v/firm-cli?label=firm-cli&color=blue)](https://pypi.org/project/firm-cli/)
[![PyPI — mcp-openclaw](https://img.shields.io/pypi/v/mcp-openclaw-extensions?label=mcp-openclaw&color=blue)](https://pypi.org/project/mcp-openclaw-extensions/)
[![CI](https://github.com/romainsantoli-web/firm-ecosystem/actions/workflows/ci.yml/badge.svg)](https://github.com/romainsantoli-web/firm-ecosystem/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/ghcr.io-mcp--openclaw-brightgreen)](https://ghcr.io/romainsantoli-web/mcp-openclaw-extensions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![MCP 2025-11-25](https://img.shields.io/badge/MCP-2025--11--25-purple.svg)](https://modelcontextprotocol.io)

</div>

---

## Why Firm?

| Problem | How Firm solves it |
|---------|-------------------|
| AI agents forget everything between sessions | **4-layer Hebbian memory** that learns, consolidates, and prunes automatically |
| Setting up multi-agent teams takes days | `firm init` generates a production-ready agent firm in seconds |
| No standard for agent-to-agent communication | **A2A Protocol RC v1.0** + **MCP 2025-11-25** — 138 tools out of the box |
| Memory solutions are cloud-only, vendor-locked | **100% local**, MIT licensed, SQLite-backed — runs on your laptop |
| No security auditing for AI agent configs | **47 security checks** across 10 audit modules (CRITICAL → MEDIUM) |

### vs. the competition

| Feature | **Firm** | mem0 | Zep | LangGraph |
|---------|----------|------|-----|-----------|
| Inter-session memory | ✅ 4-layer Hebbian | ✅ vector only | ✅ vector + graph | ❌ checkpoints only |
| Local-first (no cloud) | ✅ SQLite | ❌ cloud SDK | ❌ cloud CE | ✅ |
| MCP native | ✅ 138 tools | ❌ | ❌ | ❌ |
| A2A Protocol | ✅ v1.0 RC | ❌ | ❌ | ❌ |
| Multi-agent factory | ✅ 15 sectors | ❌ | ❌ | partial |
| Security audit tools | ✅ 47 checks | ❌ | ❌ | ❌ |
| Open source | ✅ MIT | partial | CE only | ✅ Apache-2.0 |
| Vendor lock-in | **none** | API key | API key | none |

---

## Quick-start (2 minutes)

```bash
pip install firm-cli

# Generate a fintech startup with 4 agent departments
firm init --sector fintech --size startup --output ./my-firm

# Start the MCP server (138 tools available immediately)
firm start
```

Then add to your VS Code `settings.json`:

```json
{
  "mcp.servers": {
    "firm": {
      "url": "http://127.0.0.1:8012/mcp"
    }
  }
}
```

That's it. Your agents now have persistent memory, security auditing, and inter-agent communication.

### Docker (one command)

```bash
docker compose up -d
# MCP server on :8012, Memory server on :8765
```

### Full install (with memory backend)

```bash
pip install firm-cli[full]     # includes mcp-openclaw + memory-os-ai
firm init --sector saas --size enterprise --output ./my-firm
firm start --memory             # starts memory server alongside MCP
firm memory dashboard           # view learned patterns
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Your IDE (VS Code / Cursor / Windsurf / Claude Code)        │
│   └─► firm-cli  ─────────────────────────────────────────────┤
│         │  firm init    → generate agent firms               │
│         │  firm start   → launch MCP + memory servers        │
│         │  firm memory  → inspect learned patterns           │
│         │  firm config  → manage settings                    │
└─────────┼────────────────────────────────────────────────────┘
          │
   ┌──────▼──────────────────┐    ┌──────────────────────────┐
   │  mcp-openclaw-extensions│    │  Memory-os-ai            │
   │  (MCP server :8012)     │◄──►│  (Hebbian memory :8765)  │
   │  138 tools / 29 modules │    │  4-layer CLAUDE.md       │
   │  A2A + security + audit │    │  cosine similarity       │
   └──────┬──────────────────┘    │  PII stripping           │
          │                       └──────────────────────────┘
   ┌──────▼──────────────────┐
   │  OpenClaw Gateway       │    ws://127.0.0.1:18789
   │  ┌──────────────────┐   │
   │  │  Agent Pyramid    │   │    15 sectors × 3 sizes
   │  │  (firm init)      │   │    up to 18 departments
   │  └──────────────────┘   │
   └──────┬──────────────────┘
          │
   ┌──────▼──────────────────┐
   │  ClawHub (34 skills)    │    clawhub.ai
   └─────────────────────────┘
```

---

## Table of contents

1. [Why Firm?](#why-firm)
2. [Quick-start](#quick-start-2-minutes)
3. [Architecture](#architecture)
4. [Hebbian Memory — how it works](#hebbian-memory--how-it-works)
5. [Factory — generate firms](#factory--generate-firms)
6. [MCP Tools (138)](#mcp-tools-138)
7. [Security Audit](#security-audit)
8. [Skills (ClawHub)](#skills-clawhub--34-skills)
9. [SOUL Personas](#soul-personas)
10. [CI/CD](#cicd)
11. [Configuration](#configuration)
12. [Contributing](#contributing)

---

## Hebbian Memory — how it works

Firm implements a **4-layer adaptive memory** inspired by neuroscience's Hebbian learning ("neurons that fire together wire together"):

```
Layer 4: Meta Instructions      ← rarely changes, highest authority
Layer 3: Episodic Index         ← session summaries, auto-decayed
Layer 2: Consolidated Patterns  ← learned rules, Hebbian-weighted
Layer 1: Core Identity          ← immutable project DNA
```

**Weight formula:** `new_weight = old_weight + lr × activation - decay × (1 - activation)`

- **Harvest**: collects JSONL session logs, strips PII, extracts co-activation patterns
- **Consolidation**: frequently co-activated patterns get promoted to Layer 2 as rules
- **Decay**: unused patterns gradually lose weight and get pruned
- **Drift detection**: cosine similarity against baseline catches unintended memory divergence

```bash
firm memory dashboard    # rich table of learned patterns + weights
firm memory analyze      # co-activation analysis
```

---

## Factory — generate firms

```bash
firm init --help

Options:
  --sector    generic|legal|medtech|ecommerce|fintech|saas|
              manufacturing|education|realestate|logistics|
              media|automotive|energy|hr|consulting
  --stack     typescript|python|rust|go|java|dotnet|fullstack
  --size      startup (4 depts) | scaleup (8) | enterprise (18)
  --output    Output directory (default: ./firm-output)
  --lang      en|fr
  --dry-run   Print what would be written, write nothing
  --force     Overwrite existing output directory
```

---

## MCP Tools (138)

138 tools across 29 modules, organized by category:

| Category | Count | Key capabilities |
|----------|-------|-----------------|
| **Security & Audit** | 47 | SQL injection, sandbox, secrets lifecycle, prototype pollution, HSTS, rate limiting |
| **Hebbian Memory** | 8 | Harvest, weight update, analyze, drift check, PII stripping, layer validation |
| **A2A Bridge** | 8 | Agent cards, task lifecycle, cancel, SSE subscribe, push CRUD, JWS signing |
| **Platform & Ecosystem** | 16 | Secrets v2, routing, voice, trust, firewall, RAG, cost analytics, token budget |
| **Spec Compliance** | 18 | MCP 2025-11-25 elicitation, tasks, resources, audio, prompt injection, OAuth/OIDC |
| **Infrastructure** | 16 | VS Code bridge, fleet management, delivery pipeline (GitHub/Jira/Linear/Slack) |
| **Config & Migration** | 17 | Runtime audit, gateway hardening, config migration, observability, i18n |
| **Specialized** | 8 | Agent orchestration (DAG), n8n bridge, browser audit, skill loader |

Full reference: [mcp-openclaw-extensions/README.md](mcp-openclaw-extensions/README.md)

---

## Security Audit

47 security checks across 3 severity levels:

| Severity | Count | Examples |
|----------|-------|---------|
| CRITICAL | 9 | SQL injection, sandbox off, hardcoded secrets, plugin auth bypass, exec plan mutation |
| HIGH | 19 | Gateway auth, race conditions, Node.js CVEs, shell env sanitization, webhook HMAC |
| MEDIUM | 19 | Disk budget, DM allowlist, OTEL redaction, RPC rate limiting, log redaction |

---

## Skills (ClawHub) — 34 skills

```
skills/
├── firm-orchestration/           # A2A pyramid handoff protocol
├── firm-legal-pack/              # Legal/compliance sector bundle
├── firm-medtech-pack/            # MedTech/pharma (FDA/CE/ISO 13485)
├── firm-ecommerce-pack/          # E-commerce/D2C/marketplace
├── firm-fintech-pack/            # Fintech/neobank/AML/KYC
├── firm-saas-pack/               # SaaS/PLG
├── firm-delivery-export/         # Deliverables pipeline skill
├── firm-security-audit/          # 5-step security audit sequence
├── firm-acp-bridge/              # ACP persistence + cron + locking
├── firm-hebbian-memory/          # Adaptive Hebbian memory system
├── firm-a2a-bridge/              # A2A Protocol RC v1.0 bridge (8 tools)
├── firm-spec-compliance-pack/    # MCP 2025-11-25 spec compliance (7 tools)
├── firm-prompt-security-pack/    # Prompt injection detection (2 tools)
├── firm-gateway-hardening-pack/  # Gateway auth + credentials (5 tools)
├── firm-fleet-manager-pack/      # Fleet multi-instances Gateway (6 tools)
├── firm-runtime-audit-pack/      # Runtime & config audit (7 tools)
├── firm-advanced-security-pack/  # Advanced security (8 tools)
├── firm-config-migration-pack/   # Config migration (5 tools)
├── firm-reliability-pack/        # Reliability + ADR (4 tools)
├── firm-observability-pack/      # JSONL→SQLite traces + CI (2 tools)
├── firm-memory-audit-pack/       # pgvector + knowledge graph (2 tools)
├── firm-agent-orchestration-pack/ # DAG task execution (2 tools)
├── firm-i18n-audit-pack/         # Locale scanning (1 tool)
├── firm-n8n-bridge-pack/         # n8n workflow bridge (2 tools)
├── firm-browser-audit-pack/      # Browser automation audit (1 tool)
├── firm-platform-audit-pack/     # Platform alignment 2026.2 (8 tools)
├── firm-ecosystem-audit-pack/    # Ecosystem differentiation (7 tools)
├── firm-auth-compliance-pack/    # OAuth/OIDC + compliance (8 tools)
├── firm-vs-bridge-pack/          # VS Code context sync (4 tools)
└── firm-skill-loader-pack/       # Lazy SKILL.md loading (2 tools)
```

Install all skills at once:

```bash
# After firm generation
bash ./my-firm/scripts/install-skills.sh

# Or manually via ClawHub CLI
clawhub install firm-orchestration firm-saas-pack firm-delivery-export firm-security-audit firm-acp-bridge
```

Each `SKILL.md` file is directly publishable to ClawHub with the standard YAML frontmatter.

---

## SOUL personas

Publishable to [onlycrabs.ai](https://onlycrabs.ai) registry.

```
souls/
├── firm-ceo/                # Alexandra Meridian — strategic orchestrator
├── firm-cfo/                # Marcus Venn — financial architecture
├── firm-cto/                # Soren Hales — technical excellence
├── firm-legal-analyst/      # Inés Clavero — regulatory radar
├── firm-hr-director/        # Camille Osei — people systems
├── firm-market-research/    # Élise Montblanc — competitive intelligence
├── firm-legal-status/       # Thibault Desvaux — legal status advisory
├── firm-location/           # Gabrielle Lefèvre — location strategy
└── firm-suppliers/          # Marc-Antoine Roussel — procurement
```

Each SOUL.md contains: identity, core values, communication style, decision framework,
pyramid behaviour, constraints, and sample interactions.

---

## CI/CD

| Workflow | Trigger | Description |
|----------|---------|-------------|
| [`ci.yml`](.github/workflows/ci.yml) | PR + push to main | Lint + test both packages (Python 3.11/3.12/3.13) |
| [`publish-pypi.yml`](.github/workflows/publish-pypi.yml) | Tag `v*` | Publish to PyPI (trusted publishing) |
| [`docker-ghcr.yml`](.github/workflows/docker-ghcr.yml) | Tag `v*` | Build + push Docker images to GHCR |
| [`openclaw-review.yml`](.github/workflows/openclaw-review.yml) | PR | AI-powered code review via OpenClaw Quality dept |

---

## Tests

```bash
# MCP extensions — 2583 tests
cd mcp-openclaw-extensions && pip install -r requirements-dev.txt
python -m pytest tests/ -v --cov=src --cov-fail-under=80

# firm-cli — 14 tests
cd firm-cli && pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

## Configuration

See `mcp-openclaw-extensions/.env.example` for the full list. Key variables:

```bash
MCP_EXT_HOST=127.0.0.1          # MCP server bind address
MCP_EXT_PORT=8012                # MCP server port
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:18789  # OpenClaw Gateway
GITHUB_TOKEN=<token>             # For delivery pipeline
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/romainsantoli-web/firm-ecosystem
cd firm-ecosystem
pip install -e "firm-cli[dev]"
pip install -e "mcp-openclaw-extensions[dev]"
python -m pytest mcp-openclaw-extensions/tests/ firm-cli/tests/ -v
```

---

## Security

- Timing-safe auth (`hmac.compare_digest`), 2MB request cap, 120s tool timeout
- SQL injection guard, session ID regex, path traversal blocking on all config inputs
- Tokens masked in all logs (`mask_secret()` — last 4 chars only)
- 47 automated security checks via MCP tools
- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

---

## License

MIT — see [LICENSE](LICENSE)
