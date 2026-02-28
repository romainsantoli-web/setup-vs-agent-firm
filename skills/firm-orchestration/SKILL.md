---
name: firm-orchestration
version: 1.0.0
description: >
  Pyramid multi-agent orchestration for OpenClaw: routes objectives from a CEO agent
  down through departments, services and employees via sessions_send / sessions_spawn,
  collects and merges results, enforces handoff contracts, and writes the final
  deliverable back to the originating session.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    tools:
      - sessions_list
      - sessions_send
      - sessions_spawn
      - sessions_history
    primaryEnv: ""
tags:
  - orchestration
  - multi-agent
  - a2a
  - firm
  - pyramid
  - enterprise
---

# firm-orchestration

This skill implements the **A2A (Agent-to-Agent) pyramid** pattern for OpenClaw.

## Architecture

```
CEO Agent (orchestrator)
 ├── Department Strategy
 │   └── Service Planning → Employee Analyst
 ├── Department Engineering
 │   └── Service Backend  → Employee Implementer
 ├── Department Quality
 │   └── Service Testing  → Employee Auditor
 └── Department Operations
     └── Service Release  → Employee Coordinator
```

## Usage

Send this to your OpenClaw session to trigger a full firm orchestration run:

```
@firm-orchestration run
  objective: "Build a payment API"
  departments: ["engineering", "quality"]
  delivery_format: "github_pr"
```

## Tools activated

| Tool | Purpose |
|---|---|
| `sessions_list` | Discover active department/service sessions |
| `sessions_spawn` | Spawn missing sessions per pyramid level |
| `sessions_send` | Delegate objectives down the hierarchy |
| `sessions_history` | Collect results from child sessions |

## Handoff contract

Each delegation payload follows this schema:

```json
{
  "from": "ceo",
  "to": "department:engineering",
  "objective": "...",
  "constraints": ["...", "..."],
  "definition_of_done": "...",
  "context_ref": "memory:delivery/latest",
  "reply_session": "main"
}
```

## Merge strategy

Results from all departments are:
1. Collected via `sessions_history` with a 30-second deadline
2. Deduplicated by `objective_key`
3. Merged in dependency order (Strategy → Engineering → Quality → Ops)
4. Formatted according to `delivery_format`

## Security

- All inter-session calls use `reply_session: "main"` to avoid orphaned sessions
- `sessions_spawn` is rate-limited: max 20 spawns per orchestration run
- Payloads are validated against the handoff schema before dispatch
- No external network calls — pure Gateway WebSocket routing

## Example prompt

```
Use the firm-orchestration skill to:
  objective: "Audit the authentication module"
  departments: ["quality", "engineering"]
  constraints: ["read-only access only", "no production changes"]
  definition_of_done: "Security report with CVSS scores and fix recommendations"
  delivery_format: "markdown_report"
```
