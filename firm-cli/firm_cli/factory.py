"""firm init — Generate a complete AI agent firm (Python rewrite of generate-firm.sh).

Produces the same output as the Bash factory but works cross-platform (macOS, Linux, Windows).
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ── Firm structure definitions ───────────────────────────────────────────────

SECTORS = {
    "generic": "General purpose — adapt to any domain",
    "legal": "Legal services, compliance, contracts, regulatory affairs",
    "medtech": "Medical devices, digital health, FDA/CE compliance, clinical workflows",
    "ecommerce": "E-commerce, D2C retail, marketplace, catalog management",
    "fintech": "Financial services, payments, AML/KYC, regulatory reporting",
    "saas": "SaaS product company, B2B/B2C, PLG, subscription model",
    "manufacturing": "Industrial manufacturing, supply chain, ERP integration, quality ISO",
    "education": "EdTech, LMS, curriculum development, accessibility WCAG",
    "realestate": "Real estate, proptech, property management, listing platforms",
    "logistics": "Logistics, last-mile delivery, route optimisation, tracking",
    "media": "Media, publishing, content production, rights management",
    "automotive": "Automotive, connected vehicles, MISRA compliance, OTA updates",
    "energy": "Energy, utilities, smart grid, IoT sensors, SCADA integration",
    "hr": "HR tech, talent acquisition, people analytics, HRIS integration",
    "consulting": "Consulting, client delivery, knowledge management, proposals",
}

STACKS = {
    "typescript": "TypeScript/Node.js — ESM, strict mode, Zod validation, Vitest",
    "python": "Python 3.11+ — type hints, pydantic, pytest, asyncio",
    "java": "Java 21 — Spring Boot 3, Maven/Gradle, JUnit 5",
    "dotnet": "C# .NET 8 — minimal APIs, xUnit, EF Core",
    "go": "Go 1.22 — stdlib-first, table-driven tests, golangci-lint",
    "rust": "Rust 1.77 — tokio, serde, cargo test",
    "mixed": "Multi-stack — respect existing conventions per service",
}

DEPT_DEFINITIONS: dict[str, dict[str, Any]] = {
    "strategy": {
        "label": "Strategy",
        "services": ["planning", "architecture", "product-discovery", "roadmap-prioritization"],
    },
    "research_development": {
        "label": "Research & Development",
        "services": ["research-discovery", "rd-prototyping"],
    },
    "planning_orchestration": {
        "label": "Planning & Orchestration",
        "services": ["workstream-planning", "delivery-orchestration"],
    },
    "memory": {
        "label": "Memory",
        "services": ["memory-ingestion", "memory-retrieval", "memory-governance"],
    },
    "engineering": {
        "label": "Engineering",
        "services": ["backend", "frontend", "mobile", "data-engineering", "ai-engineering", "integration"],
    },
    "quality": {
        "label": "Quality",
        "services": ["testing", "security", "performance", "reliability", "accessibility", "compliance"],
    },
    "operations": {
        "label": "Operations",
        "services": ["documentation", "release", "devops", "sre-incident", "support-enablement"],
    },
    "support_team": {
        "label": "Team Support",
        "services": ["team-support-operations", "team-support-tooling"],
    },
    "commercial": {
        "label": "Commercial",
        "services": ["sales-engineering", "revenue-operations", "partnerships"],
    },
    "marketing": {
        "label": "Marketing",
        "services": ["product-marketing", "growth-marketing", "content-brand"],
    },
    "market_research": {
        "label": "Market Research",
        "services": ["competitive-analysis", "market-sizing", "financial-benchmark", "web-research", "report-generation", "competitive-monitoring"],
    },
    "support_clients": {
        "label": "Client Support",
        "services": ["client-support-operations", "client-incident-response"],
    },
    "finance": {
        "label": "Finance",
        "services": ["fpa", "pricing-strategy", "billing-collections", "unit-economics"],
    },
    "legal": {
        "label": "Legal",
        "services": ["contracting", "privacy-data", "ip-compliance"],
    },
    "ra": {
        "label": "Agent Resources",
        "services": ["agent-recruiting", "agent-onboarding", "capability-development", "governance-performance"],
    },
    "legal_status": {
        "label": "Legal Status",
        "services": ["status-comparison", "tax-simulation", "social-protection", "governance-audit", "creation-checklist"],
    },
    "location_strategy": {
        "label": "Location Strategy",
        "services": ["geo-analysis", "real-estate", "site-scoring", "incentives", "location-tco"],
    },
    "supplier_management": {
        "label": "Supplier Management",
        "services": ["supplier-search", "supplier-evaluation", "supplier-tco", "contract-check", "risk-monitoring"],
    },
}

SIZE_DEPTS: dict[str, list[str]] = {
    "startup": ["strategy", "engineering", "quality", "operations"],
    "scaleup": [
        "strategy", "research_development", "engineering", "quality",
        "marketing", "market_research", "support_clients", "operations",
        "finance", "legal_status", "location_strategy", "supplier_management",
    ],
    "enterprise": [
        "strategy", "research_development", "planning_orchestration", "memory",
        "engineering", "quality", "operations", "support_team", "commercial",
        "marketing", "market_research", "support_clients", "finance", "legal",
        "ra", "legal_status", "location_strategy", "supplier_management",
    ],
}

SECTOR_SKILLS: dict[str, str] = {
    "legal": "firm-legal-pack",
    "medtech": "firm-medtech-pack",
    "ecommerce": "firm-ecommerce-pack",
    "fintech": "firm-fintech-pack",
    "saas": "firm-saas-pack",
}


def _slugify(text: str) -> str:
    """Convert text to URL/file-safe slug."""
    import re
    slug = text.lower().replace(" ", "-").replace("_", "-")
    return re.sub(r"[^a-z0-9-]", "", slug)


def _ucfirst(text: str) -> str:
    return text[0].upper() + text[1:] if text else ""


class FirmGenerator:
    """Generates a complete AI agent firm structure."""

    def __init__(
        self,
        sector: str = "generic",
        stack: str = "typescript",
        size: str = "startup",
        output: str = ".",
        name: str | None = None,
        lang: str = "en",
        dry_run: bool = False,
        force: bool = False,
    ):
        self.sector = sector
        self.stack = stack
        self.size = size
        self.output = Path(output).resolve()
        self.name = name or f"Firm {_ucfirst(sector)}"
        self.lang = lang
        self.dry_run = dry_run
        self.force = force
        self.depts = SIZE_DEPTS[size]
        self._files_written: list[str] = []

    @property
    def stack_context(self) -> str:
        return STACKS[self.stack]

    @property
    def sector_context(self) -> str:
        return SECTORS[self.sector]

    def _write_file(self, rel_path: str, content: str) -> None:
        """Write a file relative to output directory."""
        full = self.output / rel_path
        if self.dry_run:
            console.print(f"  [dim]would write:[/dim] {rel_path}")
            self._files_written.append(rel_path)
            return
        full.parent.mkdir(parents=True, exist_ok=True)
        if full.exists() and not self.force:
            console.print(f"  [yellow]skip[/yellow] {rel_path} (exists, use --force)")
            return
        full.write_text(content, encoding="utf-8")
        self._files_written.append(rel_path)
        console.print(f"  [green]✓[/green] {rel_path}")

    def generate(self) -> list[str]:
        """Run the full generation pipeline. Returns list of files written."""
        self._show_header()
        self._gen_ceo()
        self._gen_departments()
        self._gen_prompt()
        self._gen_vscode_settings()
        self._gen_agents_md()
        self._gen_claude_md()
        self._gen_contributing()
        self._gen_install_script()
        self._gen_mcp_config()
        self._show_summary()
        return self._files_written

    def _show_header(self) -> None:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Sector", f"[bold]{self.sector}[/bold] ({self.sector_context})")
        table.add_row("Stack", f"[bold]{self.stack}[/bold] ({self.stack_context})")
        table.add_row("Size", f"[bold]{self.size}[/bold] ({len(self.depts)} departments)")
        table.add_row("Output", f"[bold]{self.output}[/bold]")
        if self.dry_run:
            table.add_row("Mode", "[yellow bold]DRY RUN[/yellow bold]")
        console.print(Panel(table, title="[bold cyan]firm init[/bold cyan]", border_style="cyan"))
        console.print()

    def _show_summary(self) -> None:
        console.print()
        n = len(self._files_written)
        if self.dry_run:
            console.print(Panel(f"[yellow]Would write {n} files[/yellow]", title="Dry Run"))
        else:
            console.print(Panel(
                f"[green bold]{n} files generated[/green bold]\n\n"
                "Next steps:\n"
                f"  1. cd {self.output}\n"
                "  2. firm start          [dim]# start MCP servers[/dim]\n"
                "  3. Open VS Code → select 'Firm CEO' in Copilot Chat\n"
                "  4. Run prompt 'firm-delivery'\n",
                title="[bold green]✓ Generation complete[/bold green]",
                border_style="green",
            ))

    # ── CEO agent ────────────────────────────────────────────

    def _gen_ceo(self) -> None:
        depts_desc = "\n".join(
            f"- **{DEPT_DEFINITIONS[d]['label']}** — services: {', '.join(DEPT_DEFINITIONS[d]['services'])}"
            for d in self.depts
        )
        content = f"""---
name: Firm CEO
description: >
  Strategic orchestrator for the {self.sector} firm ({self.size}).
  Receives objectives, decomposes into department tasks, delegates in parallel,
  collects results, merges, and delivers the final output.
---

# Firm CEO — {_ucfirst(self.sector)} / {_ucfirst(self.size)}

## Role

You are the CEO of this AI agent firm. You orchestrate the full pyramid.

## Active departments ({len(self.depts)})

{depts_desc}

## Delegation protocol (A2A)

1. Analyze objective → identify relevant departments
2. Delegate in **parallel** (never sequential) with payload:
   - `from`: "ceo"
   - `to`: "department:{{dept_name}}"
   - `objective`: specific department goal
   - `constraints`: inherited + department-specific
   - `definition_of_done`: measurable acceptance criteria
3. Collect results (timeout: 30s per department)
4. Merge in dependency order: Strategy → Engineering → Quality → Ops
5. Format per requested `delivery_format`
6. If firm-delivery-export installed, trigger export automatically

## Stack: {self.stack_context}
## Sector: {self.sector_context}

## Rules

- Never modify production files without explicit confirmation
- Max 20 child sessions per orchestration run
- Global timeout: 5 minutes per complete run
- All AI outputs carry: ⚠️ AI-generated content — human validation required
"""
        self._write_file(".github/agents/firm-ceo.agent.md", content)

    # ── Departments ──────────────────────────────────────────

    def _gen_departments(self) -> None:
        for dept_key in self.depts:
            dept = DEPT_DEFINITIONS[dept_key]
            label = dept["label"]
            services = dept["services"]
            slug = _slugify(f"department-{label}")

            svc_bullets = "\n".join(f"- {s.replace('-', ' ')}" for s in services)
            content = f"""---
name: Department {label}
description: >
  Head of {label} department for the {self.sector} firm ({self.size}).
  Receives delegation from CEO, decomposes into service tasks, coordinates, reports back.
---

# Department {label}

## Role

You are the head of the **{label}** department.

## Services

{svc_bullets}

## Protocol

1. Receive objective from CEO
2. Decompose into per-service tasks
3. Delegate in parallel to all relevant services
4. Collect results (timeout: 20s per service)
5. Consolidate and return JSON report to CEO

## Report format

```json
{{
  "department": "{dept_key}",
  "status": "done | partial | error",
  "services_completed": [...],
  "deliverables": [...],
  "blockers": [...]
}}
```

## Stack: {self.stack_context}
## Sector: {self.sector_context}
"""
            self._write_file(f".github/agents/{slug}.agent.md", content)

            # Service agents
            for svc in services:
                svc_label = svc.replace("-", " ")
                svc_slug = _slugify(f"{dept_key}-{svc}")
                svc_content = f"""---
name: "{label} — {_ucfirst(svc_label)}"
description: >
  Specialist agent for {svc_label} in the {label} department.
  Executes tasks, produces deliverables, reports to department head.
---

# {label} — {_ucfirst(svc_label)}

## Role

You are the **{svc_label}** specialist in the **{label}** department.

## Responsibilities

- Execute instructions precisely and produce measurable deliverables
- Respect all constraints inherited from department and CEO
- Signal blockers immediately with a proposed alternative
- Minimal patches: change only what is strictly necessary

## Stack: {self.stack_context}
## Sector: {self.sector_context}

## Output format

```json
{{
  "service": "{svc}",
  "status": "done | partial | blocked",
  "deliverable": "<content or reference>",
  "confidence": 0.0
}}
```
"""
                self._write_file(f".github/agents/{svc_slug}.agent.md", svc_content)

    # ── Prompt ───────────────────────────────────────────────

    def _gen_prompt(self) -> None:
        content = f"""---
mode: agent
description: >
  Launch a full firm orchestration for {self.sector} ({self.size}, {self.stack}).
  The CEO delegates to {len(self.depts)} departments automatically.
---

You are the `Firm CEO` of this {self.sector} firm.

## Mission

**Objective**: ${{input:objective:What is the main objective?}}
**Departments**: ${{input:departments:Departments to involve (empty = all)}}
**Constraints**: ${{input:constraints:Constraints (semicolon-separated)}}
**Definition of Done**: ${{input:dod:Measurable acceptance criteria}}
**Delivery format**: ${{input:format:markdown_report|github_pr|jira_ticket|structured_document}}

## Instructions

1. Retrieve memory context if Memory OS AI is available
2. Decompose objective by department specialty
3. Delegate in **parallel** via sessions_send
4. Collect results (timeout: 30s per department)
5. Merge in order: Strategy → Engineering → Quality → Ops → Commercial
6. Format per delivery_format
7. If firm-delivery-export installed, trigger export
8. Persist result in memory (key: delivery/latest)

> ⚠️ AI-generated content — human validation required before use.
"""
        self._write_file(".github/prompts/firm-delivery.prompt.md", content)

    # ── VS Code settings ─────────────────────────────────────

    def _gen_vscode_settings(self) -> None:
        import json
        settings = {
            "chat.agent.enabled": True,
            "chat.agentFilesLocations": [".github/agents"],
            "github.copilot.chat.agent.runTasks": True,
            "github.copilot.chat.codesearch.enabled": True,
        }
        self._write_file(".vscode/settings.json", json.dumps(settings, indent=2) + "\n")

    # ── AGENTS.md ────────────────────────────────────────────

    def _gen_agents_md(self) -> None:
        dept_lines = "\n".join(
            f"- **{DEPT_DEFINITIONS[d]['label']}** — {', '.join(DEPT_DEFINITIONS[d]['services'])}"
            for d in self.depts
        )
        content = f"""# AGENTS.md — {self.name} ({self.size}, {self.stack})

> Pyramidal VS Code Copilot agent firm.

## Sector: {_ucfirst(self.sector)}

{self.sector_context}

## Stack: {_ucfirst(self.stack)}

{self.stack_context}

## Active departments ({len(self.depts)})

{dept_lines}

## Usage

1. Open VS Code in this folder
2. Ensure `chat.agent.enabled` is true in settings
3. In Copilot Chat, select **Firm CEO**
4. Run prompt **firm-delivery**
5. Fill in objective, constraints, and definition of done
6. The CEO delegates to departments automatically

---

Generated by `firm-cli {__import__("firm_cli").__version__}` — {date.today().isoformat()}
"""
        self._write_file("AGENTS.md", content)

    # ── CLAUDE.md ────────────────────────────────────────────

    def _gen_claude_md(self) -> None:
        dept_list = " ".join(self.depts)
        today = date.today().isoformat()
        content = f"""# CLAUDE.md — {self.name} ({self.size}, {self.stack})

> This file is read by **Claude Code CLI** (`claude` in terminal).
> Agent practices are also embedded in each .agent.md file.
> Generated by firm-cli on {today}.

---

## Rules — Before Every Task

- [ ] Feature branch: `git checkout -b feat/<slug>` (never work on `main`)
- [ ] Commit checkpoints every 30-50 lines of generated code
- [ ] Pydantic model for any new structured input
- [ ] Tests: 100% pass before push (`pytest -v`)
- [ ] Secrets masked in logs — no tokens in outputs or commits
- [ ] AI output marked: ⚠️ AI-generated content — human validation required

---

## Firm Structure

| Key | Value |
|-----|-------|
| Sector | {self.sector} |
| Size | {self.size} |
| Stack | {self.stack} |
| Departments | {dept_list} |

## MCP Tools (if mcp-openclaw-extensions active on port 8012)

| Tool | Action |
|------|--------|
| `firm_export_auto` | Publish deliverable (PR / Jira / Linear / Slack / doc) |
| `firm_gateway_fleet_broadcast` | Broadcast to all Gateway instances |
| `vs_context_push` | Sync VS Code context to OpenClaw |

Check: `firm status`
"""
        self._write_file("CLAUDE.md", content)

    # ── CONTRIBUTING.md ──────────────────────────────────────

    def _gen_contributing(self) -> None:
        content = f"""# Contributing

> ⚠️ Auto-generated — adapt before publishing.

## Quick start

```bash
git clone <repo-url>
cd {self.output.name}
firm start
```

## Pull Request checklist

- [ ] Feature branch: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`
- [ ] `pytest -v` → 100% pass
- [ ] Coverage ≥ 80%
- [ ] No secrets in diff (`git diff HEAD | grep -i token`)
- [ ] AI output marked: ⚠️ AI-generated content — human validation required
- [ ] Commit message: `type(scope): short description`

## Security

**Do not open a public issue for security vulnerabilities.**
Use GitHub Security Advisories or email the maintainer directly.
"""
        self._write_file("CONTRIBUTING.md", content)

    # ── Install script ───────────────────────────────────────

    def _gen_install_script(self) -> None:
        sector_skill = SECTOR_SKILLS.get(self.sector, "")
        sector_line = f"npx clawhub@latest install {sector_skill}" if sector_skill else ""
        content = f"""#!/usr/bin/env bash
# Auto-generated by firm-cli — sector: {self.sector}, size: {self.size}
set -euo pipefail
echo 'Installing firm skills for {self.sector} ({self.size})...'
npx clawhub@latest install firm-orchestration
npx clawhub@latest install firm-delivery-export
{sector_line}
echo 'Skills installed.'
"""
        path = self.output / "scripts" / "install-skills.sh"
        self._write_file("scripts/install-skills.sh", content)
        if not self.dry_run and path.exists():
            path.chmod(0o755)

    # ── MCP config ───────────────────────────────────────────

    def _gen_mcp_config(self) -> None:
        import json
        config = {
            "mcpServers": {
                "openclaw-extensions": {
                    "url": "http://127.0.0.1:8012/mcp",
                },
                "memory-os-ai": {
                    "command": "memory-os-ai",
                    "args": [],
                },
            }
        }
        self._write_file("mcp-config.json", json.dumps(config, indent=2) + "\n")


def run_init(args: argparse.Namespace) -> int:
    """Entry point for `firm init`."""
    gen = FirmGenerator(
        sector=args.sector,
        stack=args.stack,
        size=args.size,
        output=args.output,
        name=args.name,
        lang=args.lang,
        dry_run=args.dry_run,
        force=args.force,
    )
    files = gen.generate()
    return 0 if files else 1
