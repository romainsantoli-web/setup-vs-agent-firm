# Example Projects

Ready-to-run examples showing Firm in action across different sectors.

## Quick Start

Each example can be generated and started in under 2 minutes:

```bash
pip install firm-cli
cd examples/fintech-startup
bash setup.sh
```

## Available Examples

### 1. [Fintech Startup](fintech-startup/)
A 4-department AI agent firm for a neobank:
- **Product** — feature specs, user stories, competitor analysis
- **Engineering** — code review, architecture decisions, technical debt tracking
- **Security** — AML/KYC compliance, vulnerability scanning, audit trails
- **Finance** — financial modeling, regulatory reporting, risk assessment

Demonstrates: `firm init`, MCP tool calls, Hebbian memory learning from sessions.

### 2. [Legal Practice](legal-practice/)
An 8-department AI agent firm for a law practice:
- Legal research, contract review, case management
- Compliance monitoring, regulatory tracking
- Client communication, document generation

Demonstrates: sector-specific skills, SOUL personas, multi-department routing.

### 3. [SaaS Scale-up](saas-scaleup/)
A 12-department AI agent firm for a B2B SaaS company:
- Full product lifecycle: product → engineering → QA → devops → support
- Growth: marketing → sales → analytics
- Operations: HR → finance → legal → strategy

Demonstrates: enterprise-scale deployment, fleet management, delivery pipeline.

## Creating Your Own

```bash
firm init --sector <your-sector> --size <startup|scaleup|enterprise> --output ./my-firm
firm start
```

See `firm init --help` for all 15 supported sectors.
