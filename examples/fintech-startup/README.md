# Fintech Startup — Example

A complete AI agent firm for a **neobank / fintech startup** with 4 departments.

## What's inside

```
firm-output/
├── AGENTS.md                  ← routing map for all agents
├── CLAUDE.md                  ← Hebbian memory (learns from your sessions)
├── ceo.agent.md               ← CEO orchestrator
├── departments/
│   ├── engineering/            ← code review, architecture, tech debt
│   ├── product/                ← feature specs, user stories
│   ├── security/               ← AML/KYC, vulnerability scanning
│   └── finance/                ← modeling, reporting, risk
├── services/
│   └── *.agent.md              ← specialized service agents
└── scripts/
    └── install-skills.sh       ← installs ClawHub skills
```

## Quick start

```bash
bash setup.sh
firm start
```

## Example interactions

Once the MCP server is running, try these in your AI-powered IDE:

### Security audit
> "Run `openclaw_security_scan` on my OpenClaw config and report any CRITICAL findings"

### AML/KYC compliance check
> "What are the AML/KYC requirements for a European neobank? Reference the fintech skill pack"

### Architecture decision
> "Generate an ADR for choosing between PostgreSQL and DynamoDB for our transaction ledger"

### Memory in action
After a few sessions, your CLAUDE.md will automatically learn patterns like:
- "Always run security audit before deploying"
- "Prefer PostgreSQL for financial transactions"
- "AML checks are required for transactions > €10,000"

## Hebbian memory demo

```bash
# After a few coding sessions, check what Firm learned:
firm memory dashboard

# Example output:
# ┌─────────────────────────────────────────┬────────┬──────────┐
# │ Rule                                    │ Weight │ Sessions │
# ├─────────────────────────────────────────┼────────┼──────────┤
# │ Run security audit before deploy        │ 0.87   │ 12       │
# │ Use PostgreSQL for ledger tables        │ 0.73   │ 8        │
# │ KYC verification on onboarding flow     │ 0.65   │ 6        │
# └─────────────────────────────────────────┴────────┴──────────┘
```

## MCP tools used

| Tool | Purpose |
|------|---------|
| `openclaw_security_scan` | Full security audit |
| `openclaw_secrets_workflow_check` | Detect hardcoded secrets |
| `firm_adr_generate` | Generate architecture decision records |
| `openclaw_hebbian_harvest` | Ingest session logs |
| `openclaw_hebbian_weight_update` | Update learned patterns |
| `firm_export_github_pr` | Export findings as GitHub PR |
