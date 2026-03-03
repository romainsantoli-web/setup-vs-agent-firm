# SaaS Scale-up — Example

A 12-department AI agent firm for a **B2B SaaS company** in growth mode.

## Quick start

```bash
bash setup.sh
firm start --memory   # start with Hebbian memory enabled
```

## Departments (12)

| Department | Agents | Key tools |
|-----------|--------|-----------|
| Product | PM, Designer, Researcher | `firm_export_linear_issue` |
| Engineering | Lead, Backend, Frontend | `firm_adr_generate`, `openclaw_security_scan` |
| QA | QA Lead, Automation | `openclaw_ci_pipeline_check` |
| DevOps | SRE, Platform | `openclaw_gateway_probe`, `openclaw_node_version_check` |
| Security | SecOps, Compliance | All 47 security audit tools |
| Data | Analytics, ML | `openclaw_observability_pipeline` |
| Marketing | Content, Growth | `firm_export_slack_digest` |
| Sales | AE, SDR | `firm_export_document` |
| Support | L1, L2, Docs | `openclaw_skill_search` |
| HR | Recruiter, People Ops | SOUL personas |
| Finance | Controller, FP&A | `firm_export_jira_ticket` |
| Strategy | Strategy, Partnerships | `openclaw_a2a_card_generate` |

## Fleet management demo

```bash
# Check all running Gateway instances
firm status

# In VS Code, ask:
# "Broadcast a security audit across all fleet instances"
# → Uses firm_gateway_fleet_broadcast to fan out to N instances
```

## Delivery pipeline demo

```
You: "Create a Jira ticket for the authentication refactoring,
      a GitHub PR with the implementation plan, and post a
      summary to the #engineering Slack channel"

Agent: → firm_export_jira_ticket (creates ENG-1234)
       → firm_export_github_pr (creates PR #42 as draft)
       → firm_export_slack_digest (posts to #engineering)
       → All three linked with cross-references
```

## Memory evolution over time

```
Week 1: Firm learns your codebase patterns
  "Always run tests before creating PRs"
  "Use TypeScript strict mode in frontend"

Week 4: Firm consolidates team conventions
  "Architecture decisions go through ADR process"
  "Security review required for auth changes"

Week 8: Firm develops institutional knowledge
  "Q4 release freeze starts November 15"
  "Customer X requires SOC 2 compliance artifacts"
```
