# Legal Practice — Example

An 8-department AI agent firm for a **law practice** — contract review, compliance,
research, and client management.

## Quick start

```bash
bash setup.sh
firm start
```

## Departments (8)

| Department | Role |
|-----------|------|
| Legal Research | Case law search, precedent analysis, jurisdiction mapping |
| Contract Review | Clause analysis, risk scoring, redline suggestions |
| Compliance | GDPR, CCPA, SOX monitoring and audit |
| Litigation | Case strategy, timeline management, evidence organization |
| Corporate | M&A due diligence, governance, board resolutions |
| Client Relations | Intake, communication, billing, satisfaction tracking |
| HR | Attorney recruitment, bar compliance, CLE tracking |
| Finance | Trust accounting, billing, collections, P&L |

## Skills used

- `firm-legal-pack` — Legal/compliance sector bundle
- `firm-security-audit` — Data protection audit
- `firm-delivery-export` — Export memos, contracts, and briefs

## Example: Contract review workflow

```
You: "Review the attached SaaS agreement for liability and indemnification issues"

Agent (Legal Research dept):
  → Searches precedents for SaaS liability clauses
  → Cross-references with jurisdiction-specific rules

Agent (Contract Review dept):
  → Identifies 3 problematic clauses
  → Suggests redline amendments
  → Flags unlimited liability exposure in Section 8.2

Agent (CEO):
  → Consolidates findings into a client-ready memo
  → Exports via firm_export_document
```

## Memory learning

After reviewing multiple contracts, Firm learns patterns like:
- "Section 8 typically contains liability caps — always review"
- "Force majeure clauses need COVID-era updates"
- "EU contracts require GDPR-specific data processing addendum"
