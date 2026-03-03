# MCP Tool Reference — v3.3.0

> Auto-generated from source code. 138 tools across 26 categories.

---

## Categories

- [a2a](#a2a) (8 tools)
- [acp](#acp) (7 tools)
- [auth_compliance](#auth_compliance) (2 tools)
- [browser_automation](#browser_automation) (1 tools)
- [compliance_medium](#compliance_medium) (6 tools)
- [ecosystem](#ecosystem) (7 tools)
- [export](#export) (6 tools)
- [fleet](#fleet) (6 tools)
- [hebbian_memory](#hebbian_memory) (8 tools)
- [i18n](#i18n) (1 tools)
- [legal_status](#legal_status) (5 tools)
- [location_strategy](#location_strategy) (5 tools)
- [market_research](#market_research) (6 tools)
- [memory](#memory) (2 tools)
- [observability](#observability) (2 tools)
- [orchestration](#orchestration) (2 tools)
- [performance](#performance) (2 tools)
- [platform](#platform) (9 tools)
- [procurement](#procurement) (5 tools)
- [prompt_security](#prompt_security) (2 tools)
- [reliability](#reliability) (4 tools)
- [security](#security) (9 tools)
- [spec_compliance](#spec_compliance) (7 tools)
- [uncategorized](#uncategorized) (20 tools)
- [vs_bridge](#vs_bridge) (4 tools)
- [workflow_automation](#workflow_automation) (2 tools)

---

## a2a

### `openclaw_a2a_cancel_task`

Cancel a running A2A task (RC v1.0 CancelTask). Error if task is in terminal state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | ✅ | Task ID to cancel. |

### `openclaw_a2a_card_generate`

Generate .well-known/agent-card.json from a SOUL.md file. RC v1.0 compliant with extensions, JCS+JWS signing, defaultInputModes/defaultOutputModes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_url` | string | ✅ | Base URL where this agent is reachable. |
| `capabilities` | object | — | A2A capabilities. |
| `default_input_modes` | array | — | Default input MIME types. |
| `default_output_modes` | array | — | Default output MIME types. |
| `extensions` | array | — | Extension declarations. |
| `output_path` | string | — | Optional path to write the Agent Card JSON. |
| `security_schemes` | object | — | Security scheme definitions. |
| `sign` | boolean | — | Sign card with JCS+JWS. |
| `signing_key` | string | — | Signing key (masked in output). |
| `soul_path` | string | ✅ | Path to the SOUL.md file. |

### `openclaw_a2a_card_validate`

Validate an A2A Agent Card against RC v1.0 spec. Detects deprecated v0.4.0 patterns (kind discriminator).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_json` | object | — | Inline Agent Card dict. |
| `card_path` | string | — | Path to an agent-card.json file. |

### `openclaw_a2a_discovery`

Discover agents via Agent Cards or local SOUL.md scan (RC v1.0). Probes .well-known/agent-card.json.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_reachability` | boolean | — | Verify reachability. |
| `souls_dir` | string | — | Local SOUL.md directory. |
| `urls` | array | — | Agent URLs to probe. |

### `openclaw_a2a_push_config`

CRUD for push notification webhooks (RC v1.0). Create/Get/List/Delete push configs for tasks.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | — | — |
| `auth_token` | string | — | Bearer token. |
| `config_id` | string | — | Config ID (for get/delete). |
| `task_id` | string | ✅ | Task to configure. |
| `webhook_url` | string | — | Webhook URL (for create). |

### `openclaw_a2a_subscribe_task`

Subscribe to task updates via SSE (RC v1.0 SubscribeToTask). Streams TaskStatusUpdateEvent and TaskArtifactUpdateEvent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `callback_url` | string | — | Optional callback URL. |
| `task_id` | string | ✅ | Task ID to subscribe to. |

### `openclaw_a2a_task_send`

Send a message/task to an A2A agent (RC v1.0 SendMessage). Typed parts (TextPart/FilePart/DataPart), contextId multi-turn support.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_url` | string | ✅ | URL of the target A2A agent. |
| `blocking` | boolean | — | Wait for completion. |
| `context_id` | string | — | Context ID for multi-turn grouping. |
| `message` | string | ✅ | Text message to send. |
| `metadata` | object | — | Optional metadata. |

### `openclaw_a2a_task_status`

Get task status (GetTask) or list tasks (ListTasks). RC v1.0 with contextId filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context_id` | string | — | Filter by context. |
| `include_history` | boolean | — | Include message history. |
| `task_id` | string | — | Specific task ID. |

---

## acp

### `acp_session_list_active`

Lists all persisted ACP sessions with their age and status (active/stale).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_stale` | boolean | — | Include sessions older than 24h. Default: false. |

### `acp_session_persist`

Persists an ACP run_id → gateway_session_key mapping to disk. Gap C4: ACP bridge sessions are in-memory only — a crash loses all sessions. Call immediately when an ACP session is created. Uses atomic file write.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gateway_session_key` | string | ✅ | OpenClaw Gateway session key. |
| `metadata` | object | — | Optional metadata dict. |
| `run_id` | string | ✅ | ACP run ID. |

### `acp_session_restore`

Reloads ACP sessions from disk after a bridge crash or restart. Purges stale sessions (> max_age_hours) automatically. Call on bridge startup to restore all in-flight sessions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `max_age_hours` | integer | — | Sessions older than this are purged. Default: 24. |

### `fleet_cron_schedule`

Schedules a cron task on the main session, bypassing sandbox denylist. Gap H4: cron tools are on the denylist in Docker sessions, blocking autonomous scheduled workflows. Enforces strict command allowlist and blocklist for safety.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | ✅ | Command to schedule. Only [a-zA-Z0-9 /._-=] allowed. |
| `description` | string | — | Human-readable description of the task. |
| `schedule` | string | ✅ | Cron expression (5 fields, e.g. '0 9 * * 1-5'). |
| `session` | string | — | Target session. Must be 'main' (cron blocked in sandbox). |

### `fleet_session_inject_env`

Broadcasts provider env vars (API keys, model config) to all non-main Gateway sessions. Gap H3: isolated spawn/cron sessions cannot access provider env vars, blocking LLM calls. Enforces a strict key allowlist. Masks secrets in all logs and return values.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `allowlist_keys` | array | — | Extra env var keys to allow beyond the built-in allowlist. |
| `dry_run` | boolean | — | Validate without sending. Default: false. |
| `env_vars` | object | ✅ | Dict of env var key → value to inject. |
| `filter_tags` | array | — | Only target fleet instances with these tags. |

### `openclaw_acpx_version_check`

Checks ACPX plugin version pin (>= 0.1.15) and streaming mode (final_only). 2026.3.1 broke ACPX < 0.1.15 due to the new task streaming protocol. Returns: version status, streaming mode recommendation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json (default: ~/.openclaw/openclaw.json). |

### `openclaw_workspace_lock`

Advisory file lock with timeout and owner tracking. Gap H5: race condition in shared-workspace read/modify/write — multiple agent sessions can corrupt shared resources. Actions: acquire / release / status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✅ | Lock action. |
| `owner` | string | ✅ | Lock owner identifier (e.g. session ID, agent name). |
| `path` | string | ✅ | Workspace resource path to lock. No '..' allowed. |
| `timeout_s` | number | — | Max seconds to wait for lock acquisition (1-300). Default: 30. |

---

## auth_compliance

### `openclaw_oauth_oidc_audit`

Audit OAuth 2.1 / OIDC Discovery compliance (MCP 2025-06-18 / 2025-11-25). Checks issuer, PKCE S256, Protected Resource Metadata (RFC 9728), token validation, scope enforcement, resource indicators (RFC 8707).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_token_scope_check`

Check if OAuth scopes properly restrict tool access. Verifies each tool has scope requirements, detects wildcards, and identifies unscoped tools.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

---

## browser_automation

### `openclaw_browser_context_check`

Validates Playwright/Puppeteer headless browser configuration for agent use. Scans for dangerous launch args (--no-sandbox, remote debugging), checks headless mode, timeouts, viewport, and user data isolation. Gap T10: browser automation audit.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_deps` | boolean | — | Whether to check package.json for browser deps. Default: true. |
| `config_override` | object | — | Optional config dict to validate directly (skip file scan). |
| `workspace_path` | string | ✅ | Root of the workspace to scan. |

---

## compliance_medium

### `openclaw_agent_identity_audit`

Audit agent decentralized identity (DID) — format, verification methods, signing, federation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

### `openclaw_circuit_breaker_audit`

Audit circuit breaker / resilience configuration for external calls — timeouts, retries, fallback.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

### `openclaw_gdpr_residency_audit`

Audit GDPR compliance and data residency — legal basis, retention, PII fields, cross-border transfers.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

### `openclaw_model_routing_audit`

Audit multi-model routing — strategy, fallback chain, cost caps, provider diversity.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

### `openclaw_resource_links_audit`

Audit MCP resource links in tool results — URI validation, MIME types, subscriptions, templates.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

### `openclaw_tool_deprecation_audit`

Audit tool deprecation lifecycle — sunset dates, replacements, circular chains.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file (optional, defaults to ./openclaw.json). |

---

## ecosystem

### `openclaw_context_health_check`

Context rot / cognitive health detection. Checks token utilization, session age, turn count, compression ratio, recovery recommendations. Gap G23.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |
| `session_data` | object | — | Session data with tokensUsed, contextWindow, createdAt, turns. |

### `openclaw_cost_analytics`

Usage/cost tracking and analysis. Estimates cost per session, checks budget thresholds, analyzes tool call patterns. Gap G27.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |
| `session_data` | object | — | Session data with model, tokens, toolCalls, budget. |

### `openclaw_mcp_firewall_check`

MCP Gateway firewall policy audit. Checks tool allowlists, argument sanitization, per-tool rate limits, secret leakage prevention, request size limits. Gap G21.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_provenance_tracker`

Cryptographic audit trail / provenance tracking. Actions: append (hash chain entry), verify (integrity check), status, export. Gap G24.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | — | — |
| `algorithm` | string | — | — |
| `chain_path` | string | — | Export file path. |
| `entry` | object | — | Provenance entry: intent, agent, action, inputs, outputs. |

### `openclaw_rag_pipeline_check`

RAG pipeline health & configuration audit. Checks embedding model, vector store, chunk settings, retrieval top-K, index freshness. Gap G22.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_sandbox_exec_check`

Sandbox execution isolation audit. Checks sandbox mode, resource limits, filesystem restrictions, network policy, timeout enforcement. Gap G26.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_token_budget_optimizer`

Token optimization analysis. Finds compression opportunities, prompt deduplication, caching improvements, tool result savings. Gap G25.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |
| `session_data` | object | — | Session data with tokensUsed, messages, cache stats. |

---

## export

### `firm_export_auto`

Auto-route firm workflow output to the correct export target (GitHub PR, Jira, Linear, Slack, or local document) based on delivery_format. Main entrypoint for firm-delivery-export.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | ✅ | — |
| `delivery_format` | string | ✅ | — |
| `departments` | array | — | — |
| `github_base` | string | — | — |
| `github_repo` | string | — | owner/repo (for github_pr) |
| `github_reviewers` | array | — | — |
| `jira_project_key` | string | — | — |
| `linear_team_id` | string | — | — |
| `objective` | string | ✅ | — |
| `slack_mention_users` | array | — | — |

### `firm_export_document`

Write firm workflow output to a local Markdown document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | ✅ | — |
| `departments` | array | — | — |
| `format` | string | — | — |
| `objective` | string | ✅ | — |
| `output_path` | string | — | — |

### `firm_export_github_pr`

Create a GitHub draft PR from firm workflow output. Always adds needs-review + ai-generated labels. Never auto-merges.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base` | string | — | — |
| `branch` | string | — | — |
| `content` | string | ✅ | — |
| `departments` | array | — | — |
| `draft` | boolean | — | — |
| `labels` | array | — | — |
| `objective` | string | ✅ | — |
| `repo` | string | ✅ | — |
| `reviewers` | array | — | — |
| `title` | string | — | — |

### `firm_export_jira_ticket`

Create a Jira issue from firm workflow output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `components` | array | — | — |
| `content` | string | ✅ | — |
| `departments` | array | — | — |
| `issue_type` | string | — | — |
| `labels` | array | — | — |
| `objective` | string | ✅ | — |
| `priority` | string | — | — |
| `project_key` | string | ✅ | — |

### `firm_export_linear_issue`

Create a Linear issue from firm workflow output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | ✅ | — |
| `departments` | array | — | — |
| `objective` | string | ✅ | — |
| `priority` | integer | — | — |
| `team_id` | string | ✅ | — |

### `firm_export_slack_digest`

Post a formatted firm delivery digest to Slack via webhook.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | — | — |
| `content` | string | ✅ | — |
| `departments` | array | — | — |
| `mention_users` | array | — | — |
| `objective` | string | ✅ | — |

---

## fleet

### `firm_gateway_fleet_add`

Register a new OpenClaw Gateway instance in the fleet. Verifies connectivity before saving.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `department` | string | — | — |
| `http_url` | string | ✅ | — |
| `name` | string | ✅ | — |
| `tags` | array | — | — |
| `token` | string | — | — |
| `ws_url` | string | ✅ | — |

### `firm_gateway_fleet_broadcast`

Broadcast a message to all (or filtered) Gateway instances. Useful for fleet-wide announcements and multi-department orchestration kickoffs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter_department` | string | — | — |
| `filter_tag` | string | — | — |
| `message` | string | ✅ | — |
| `require_all_success` | boolean | — | — |
| `session` | string | — | — |

### `firm_gateway_fleet_list`

List all registered Gateway instances with their configuration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter_department` | string | — | — |
| `filter_tag` | string | — | — |

### `firm_gateway_fleet_remove`

Remove a Gateway instance from the fleet registry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ | — |

### `firm_gateway_fleet_status`

Health check all registered OpenClaw Gateway instances. Runs parallel /health checks and returns latency, version and session counts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter_department` | string | — | Filter by firm department |
| `filter_tag` | string | — | Filter by tag |

### `firm_gateway_fleet_sync`

Sync configuration or skills across all fleet instances in parallel.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_patch` | object | — | — |
| `dry_run` | boolean | — | — |
| `filter_department` | string | — | — |
| `filter_tag` | string | — | — |
| `skill_slugs` | array | — | — |

---

## hebbian_memory

### `openclaw_hebbian_analyze`

Analyze co-activation patterns from harvested sessions. Uses Jaccard similarity for tag co-occurrence and rule co-activation. Returns top pattern candidates. CDC §4.3 clustering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `db_path` | string | — | SQLite database path. |
| `min_cluster_size` | integer | — | Min sessions to form a pattern. Default: 5. |
| `since_days` | integer | — | Look back N days. Default: 90. |

### `openclaw_hebbian_decay_config_check`

Validate Hebbian parameters: learning_rate, decay, poids_min/max, consolidation thresholds (episodic→emergent, emergent→strong). CDC §4.3.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_data` | object | — | Inline config dict (for testing). |
| `config_path` | string | — | Path to OpenClaw config JSON. |

### `openclaw_hebbian_drift_check`

Detect Claude.md semantic drift vs a baseline using TF-IDF cosine similarity. Alerts if similarity drops below threshold (default 0.7). CDC §5.1 anti-dérive.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `baseline_path` | string | — | Path to baseline Claude.md. |
| `claude_md_path` | string | ✅ | Path to current Claude.md. |
| `threshold` | number | — | Alert if similarity < threshold. Default: 0.7. |

### `openclaw_hebbian_harvest`

Ingest JSONL session logs into the local Hebbian SQLite database. PII/secrets are stripped before storage (CDC §5.2). Supports session summary, tags, quality score, rule activations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `claude_md_path` | string | — | Optional Claude.md path for rule activation matching. |
| `db_path` | string | — | SQLite database path. Default: ~/.openclaw/hebbian.db. |
| `max_lines` | integer | — | Max lines to ingest. Default: 50000. |
| `session_jsonl_path` | string | ✅ | Path to JSONL file with session data. |

### `openclaw_hebbian_layer_validate`

Validate the 4-layer structure of a Hebbian-augmented Claude.md: CORE (L1), CONSOLIDATED PATTERNS (L2), EPISODIC INDEX (L3), META (L4). CDC §3.3.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `claude_md_path` | string | ✅ | Path to Claude.md file. |

### `openclaw_hebbian_pii_check`

Audit PII stripping configuration: regex patterns (email, phone, IP, API keys), secret detection, embedding rotation policy, access restriction. CDC §5.2.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_data` | object | — | Inline config dict (for testing). |
| `config_path` | string | — | Path to OpenClaw config JSON. |

### `openclaw_hebbian_status`

Dashboard: total sessions, Layer 2 rule weights, atrophy/promotion candidates, last harvest timestamp, weight update history. CDC §7 monitoring.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `claude_md_path` | string | — | Claude.md path for reading current weights. |
| `db_path` | string | — | SQLite database path. |

### `openclaw_hebbian_weight_update`

Compute or apply Hebbian weight updates on Layer 2 rules in Claude.md. Uses the formula: new = old + (lr × activation) - (decay × (1-activation)). Default dry_run=True (simulation only). CDC §4.3 + §4.4.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `claude_md_path` | string | ✅ | Path to Claude.md file. |
| `db_path` | string | — | SQLite database path. |
| `decay` | number | — | Atrophy rate. Default: 0.02. |
| `dry_run` | boolean | — | Simulate only (true) or write changes (false). Default: true. |
| `learning_rate` | number | — | Reinforcement rate. Default: 0.05. |

---

## i18n

### `openclaw_i18n_audit`

Audits internationalization files for missing keys, empty values, interpolation mismatches, and ICU format issues. Gap T5/issue #3460: i18n audit was most-requested feature (71 comments).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_locale` | string | — | Reference locale. Default: 'en'. |
| `file_format` | string | — | Translation file format. Default: json. |
| `locale_dir` | string | — | Path to locale directory (relative to project). Auto-detected if omitted. |
| `project_path` | string | ✅ | Root directory of the project. |

---

## legal_status

### `openclaw_legal_creation_checklist`

Post-creation compliance checklist — steps, costs, timeline, and annual obligations for the chosen legal form.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `geography` | string | — | Country/region of creation |
| `legal_form` | string | — | Legal form (SAS, SARL, etc.) |
| `sector` | string | — | Business sector |

### `openclaw_legal_governance_audit`

Governance structure audit — recommends statutory clauses, pactes d'associés, and governance organs based on legal form and investor involvement.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `founders` | integer | — | Number of founders |
| `has_investors` | boolean | — | Are there external investors? |
| `legal_form` | string | — | Legal form (SAS, SARL, etc.) |
| `specific_clauses` | array | — | Specific clauses to evaluate |

### `openclaw_legal_social_protection`

Social protection analysis by status — TNS vs assimilé salarié vs micro-entrepreneur. Compares charges, retirement, health, and unemployment coverage.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_options` | boolean | — | Include comparison with all regimes? |
| `salary` | number | — | Annual salary/revenue base (€) |
| `status` | string | — | Social status: TNS, assimile_salarie, TNS_micro |

### `openclaw_legal_status_compare`

Compare legal forms (SAS, SARL, SASU, EURL, etc.) with multi-criteria scoring matrix. Analyzes liability, tax regime, social charges, fundraising flexibility, and governance.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `criteria_weights` | object | — | Custom weights for scoring criteria |
| `founders` | integer | — | Number of founders/associates |
| `fundraising` | boolean | — | Planning to raise funds? |
| `project_type` | string | — | Type of project (startup, freelance, holding, etc.) |
| `revenue_y1` | number | — | Expected revenue Year 1 (€) |
| `sector` | string | — | Business sector |

### `openclaw_legal_tax_simulate`

Tax simulation IS vs IR over 3-5 years. Includes salary/dividend optimization, holding structure benefits, and effective tax rate calculation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dividends` | number | — | Target annual dividends (€) |
| `growth_rate` | number | — | Annual revenue growth rate (0.1 = 10%) |
| `holding` | boolean | — | Include holding structure (régime mère-fille)? |
| `horizon_years` | integer | — | Simulation horizon in years (1-10) |
| `legal_form` | string | — | Legal form (SAS, SARL, SASU, EURL, SA, MICRO) |
| `revenue` | number | — | Annual revenue Year 1 (€) |
| `salary` | number | — | Annual gross salary (€) |

---

## location_strategy

### `openclaw_location_geo_analysis`

Geo-economic analysis of candidate cities — talent pools, transport, ecosystem, infrastructure, quality of life. Compares multiple zones.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cities` | array | ✅ | List of cities/zones to analyze |
| `headcount` | integer | — | Current/planned headcount |
| `priorities` | array | — | Priority criteria |
| `sector` | string | — | Business sector |

### `openclaw_location_incentives`

Tax incentives and aid programs by territory — ZFU, ZRR, BER, CIR, JEI, BPI, FEDER. Matches company profile to available programs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_type` | string | — | Company type: startup, scaleup, enterprise |
| `headcount` | integer | — | Number of employees |
| `sector` | string | — | Business sector |
| `zone` | string | — | Zone/city to check for incentives |

### `openclaw_location_real_estate`

Real estate market intelligence — availability, pricing per sqm, coworking rates, trends by zone. Filters by budget and surface.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `budget_max` | number | — | Maximum monthly budget (€) |
| `property_type` | string | — | Type: bureau, coworking, entrepot, commerce, mixte |
| `surface_max` | integer | — | Maximum surface in sqm |
| `surface_min` | integer | — | Minimum surface in sqm |
| `zone` | string | — | Zone/region to search (e.g., 'Île-de-France', 'Lyon') |

### `openclaw_location_site_score`

Multi-criteria site scoring with 20+ weighted criteria. Compares sites on transport, talent, cost, ecosystem, and more. Outputs ranked matrix.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scores` | object | — | Custom scores per site: {site: {criterion: score(1-10)}} |
| `sites` | array | ✅ | List of sites to score |
| `weights` | object | — | Custom weights per criterion: {criterion: weight} |

### `openclaw_location_tco_simulate`

Total Cost of Occupation simulation over 3-5 years. Includes rent, charges, CFE, insurance, maintenance. Compares multiple sites.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `annual_rent_increase` | number | — | Expected annual rent increase (0.03 = 3%) |
| `headcount` | integer | — | Number of employees (for per-capita cost) |
| `horizon_years` | integer | — | Simulation horizon (1-10 years) |
| `sites` | array | ✅ | List of sites to compare |
| `surface` | integer | — | Surface in sqm |

---

## market_research

### `openclaw_market_competitive_analysis`

Full competitive landscape analysis. Produces feature matrix, SWOT per competitor, and positioning map framework. Accessible to all departments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `competitors` | array | — | List of competitor names to analyze |
| `criteria` | array | — | Comparison criteria (default: standard 12 criteria) |
| `geography` | string | — | Geographic scope (default: Global) |
| `include_positioning` | boolean | — | Include positioning map |
| `include_swot` | boolean | — | Include SWOT analysis per competitor |
| `our_product` | string | — | Our product name for comparison row |
| `sector` | string | ✅ | Target market sector (e.g. 'SaaS project management') |

### `openclaw_market_financial_benchmark`

Financial benchmarking — unit economics (CAC, LTV, ARPU, churn), pricing analysis, revenue comparisons. Cross-references with CFO data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `competitors` | array | — | Competitor names |
| `include_pricing` | boolean | — | Include pricing analysis |
| `metrics` | array | — | Metrics to benchmark (CAC, LTV, churn, ARPU, etc.) |
| `our_data` | object | — | Our financial data for comparison |
| `sector` | string | ✅ | Target market sector |

### `openclaw_market_report_generate`

Generate a complete professional market research report in Markdown. Structured for cross-department readability: CEO (executive summary), CFO (financial), CTO (tech), Marketing (positioning), Commercial (battlecards).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | object | — | Pre-collected research data |
| `include_toc` | boolean | — | Include table of contents |
| `language` | string | — | Report language |
| `output_path` | string | — | Output file path (auto-generated if omitted) |
| `sections` | array | — | Sections to include (default: all 9 sections) |
| `title` | string | ✅ | Report title |

### `openclaw_market_research_monitor`

Continuous competitive monitoring. Actions: add/remove competitors, log market events, check watchlist status, export monitoring data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | — | Monitoring action |
| `competitor` | string | — | Competitor name |
| `notes` | string | — | Event notes (for 'update' action) |
| `watch` | array | — | Items to watch (pricing, features, funding, headcount, etc.) |

### `openclaw_market_sizing`

TAM/SAM/SOM market sizing with top-down and bottom-up approaches. Includes growth analysis, drivers, and inhibitors with confidence scoring.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `approach` | string | — | Sizing approach |
| `geography` | string | — | Geographic scope (default: Global) |
| `horizon_years` | integer | — | Forecast horizon in years |
| `known_data` | object | — | Pre-existing data points (market size, CAGR, etc.) |
| `sector` | string | ✅ | Target market sector |
| `target_segment` | string | — | Specific target segment |

### `openclaw_market_web_research`

Structured web research and OSINT intelligence gathering. Multi-source (Crunchbase, LinkedIn, G2, news...) with confidence scoring.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `competitor` | string | — | Specific competitor to research |
| `max_results` | integer | — | Maximum results |
| `query` | string | ✅ | Research query |
| `sources` | array | — | OSINT sources to use (crunchbase, linkedin, g2, news, etc.) |

---

## memory

### `openclaw_knowledge_graph_check`

Audits knowledge graph integrity: backend validation, TTL policy, orphan node detection, cycle detection, density metrics, and backup configuration. Gap T9/issue #7783.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to OpenClaw config JSON. |
| `graph_data_path` | string | — | Optional path to JSON graph export for deep analysis. |

### `openclaw_pgvector_memory_check`

Validates pgvector configuration for semantic memory: index type (HNSW recommended), dimensions, distance metric, HNSW params (M, ef_construction), and connection string credential exposure. Gap T3/issue #15093.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to OpenClaw config JSON. |
| `connection_string` | string | — | Optional PostgreSQL connection string to validate. |

---

## observability

### `openclaw_ci_pipeline_check`

Validates CI workflow completeness: checks that .github/workflows/ contains lint, test, and secrets scanning steps. Also checks recommended steps (coverage, type_check). Gap T6: no CI validation tool existed.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ci_dir` | string | — | Relative path to CI directory. Default: .github/workflows. |
| `repo_path` | string | ✅ | Root of the repository to check. |

### `openclaw_observability_pipeline`

Ingests JSONL structured logs/traces (OpenTelemetry format) into a local SQLite database for offline analysis. Handles trace_id/span_id deduplication, batch inserts, and flexible field extraction. Gap T1: no observability pipeline existed.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `db_path` | string | — | Path to SQLite database. Default: ~/.openclaw/traces.db. |
| `jsonl_path` | string | ✅ | Path to the JSONL file to ingest. |
| `max_lines` | integer | — | Max lines to ingest (safety limit). Default: 50000. |
| `table_name` | string | — | Table name. Default: 'traces'. |

---

## orchestration

### `openclaw_agent_team_orchestrate`

Execute a task DAG across the agent fleet with parallel layer execution, dependency resolution (topological sort), and configurable result aggregation (collect/vote/first_success). Gap T4/issue #10010: multi-agent coordination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `aggregation_strategy` | string | — | — |
| `objective` | string | — | Human-readable orchestration objective. |
| `tasks` | array | ✅ | Task list with id, agent, action, params, depends_on. |
| `timeout_s` | number | — | Timeout in seconds. Default: 120. |

### `openclaw_agent_team_status`

Check status of running or completed fleet orchestrations. Returns task progress, layer execution state, elapsed time.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | string | — | Specific orchestration ID. If omitted, lists all. |

---

## performance

### `openclaw_skill_lazy_loader`

Lazy-loads SKILL.md metadata (YAML front-matter) without parsing full content. Caches for 5 minutes. Supports per-skill or bulk loading. Gap T7/issue #26301: reduces startup time for large skill catalogs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `refresh` | boolean | — | Force cache refresh. Default: false. |
| `skill_name` | string | — | Specific skill to load. Omit to load all. |
| `skills_dir` | string | ✅ | Directory containing skill subdirectories. |

### `openclaw_skill_search`

Search skills by keyword/tags across all SKILL.md files. Returns relevance-ranked results with metadata. Uses the lazy loader cache for performance.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Search query. |
| `skills_dir` | string | ✅ | Directory containing skill subdirectories. |
| `tags` | array | — | Optional tag filter. |

---

## platform

### `openclaw_adaptive_thinking_check`

Checks Claude 4.6 model configs for correct adaptive thinking defaults (2026.3.1). Detects disabled/low thinking modes that degrade reasoning quality. Validates both agents.defaults and per-agent overrides.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_agent_routing_check`

Validate agent routing bindings (2026.2.26+). Checks default route, scope isolation, circular routing. Gap G13.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_autoupdate_check`

Self-update supply chain integrity check (2026.2.22+). Checks update channel, signature verification, rollout delay, rollback. Gap G16.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_content_boundary_check`

Content boundary & anti-prompt-injection audit (2026.2+). Checks wrapExternalContent, wrapWebContent, toolResult stripping, content boundary markers. Gap G19.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_plugin_sdk_check`

Plugin SDK integrity validation (2026.1.16+). Checks plugin hooks, permissions, integrity hashes, package install restrictions. Gap G17.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_secrets_v2_audit`

Audit the OpenClaw secrets v2 lifecycle (2026.2.26+). Checks external provider, rotation policy, audit log, runtime snapshots, and hardcoded secret detection. Gap G12.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |
| `secrets_config_path` | string | — | Secrets-specific config. |

### `openclaw_sqlite_vec_check`

SQLite-vec memory backend validation (2026.1.12+). Checks backend config, db path, embedding model, chunking, index settings, lazy sync. Gap G20.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_trust_model_check`

Validate trust model and multi-user heuristics (2026.2.24+). Checks multi-user DM scope, trust model, gateway hardening. Gap G15.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

### `openclaw_voice_security_check`

TTS/voice channel security audit (2026.2.24+). Checks provider auth, rate limits, SSML injection, voice channel isolation. Gap G14.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | OpenClaw config path. |

---

## procurement

### `openclaw_supplier_contract_check`

Contract clause analysis — checks SLA, penalties, data protection (DPA), reversibility, IP, NDA, and more against best practices.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contract_type` | string | — | Type: SaaS, services, hardware, etc. |
| `existing_clauses` | array | — | Clauses already present in the contract |
| `requirements` | array | — | Specific contract requirements |
| `supplier` | string | — | Supplier name |

### `openclaw_supplier_evaluate`

Multi-criteria supplier evaluation with 15+ weighted criteria. Scores quality, price, delivery, support, security, and more. Outputs ranked matrix.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `criteria` | object | — | Custom weights: {criterion: weight} |
| `scores` | object | — | Custom scores: {supplier: {criterion: score(1-10)}} |
| `suppliers` | array | ✅ | List of suppliers to evaluate |

### `openclaw_supplier_risk_monitor`

Continuous supplier risk monitoring — add/remove/update/status/export watchlist. Tracks financial, dependency, geopolitical, and service level risks.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | — | Action: add, remove, update, status, export |
| `notes` | string | — | Notes about the supplier |
| `supplier` | string | — | Supplier name |
| `watch` | array | — | Risk categories to watch: financial, dependency, geopolitical, service_level, security, supply_chain, regulatory, reputation |

### `openclaw_supplier_search`

Market-wide supplier sourcing — identifies potential suppliers by category, budget, geography. Provides recommended sources and methodology.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `budget_max` | number | — | Maximum budget (€/month or €/unit) |
| `category` | string | — | Supplier category: saas, cloud, services, hardware, office, logistics, raw_materials, marketing, consulting, telecom, insurance, accounting |
| `geography` | string | — | Geography preference |
| `query` | string | — | Search query / description of need |
| `requirements` | array | — | Specific requirements |
| `users` | integer | — | Number of users (for SaaS) |

### `openclaw_supplier_tco_analyze`

Total Cost of Ownership analysis over 3-5 years. Includes license, integration, training, support, migration, and exit costs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `horizon_years` | integer | — | TCO horizon in years |
| `include_hidden_costs` | boolean | — | Include integration, training, exit costs? |
| `suppliers` | array | ✅ | Suppliers to compare |
| `unit_prices` | object | — | Monthly unit prices: {supplier: price} |
| `volume` | integer | — | Number of units/licenses/users |

---

## prompt_security

### `openclaw_prompt_injection_batch`

Batch scan multiple text inputs for injection patterns. Accepts a list of {id, text} objects and returns per-item results with severity and hit counts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `items` | array | ✅ | List of {id, text} objects to scan |

### `openclaw_prompt_injection_check`

Scan text for prompt injection and jailbreak patterns. Detects 16 pattern families including ChatML injection, role reassignment, memory reset, system prompt exfiltration, encoding evasion, and JSON boundary escape.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context` | string | — | Where the text comes from (user_input, tool_output, etc.) |
| `text` | string | ✅ | Text to scan for injection patterns |

---

## reliability

### `firm_adr_generate`

Generates a structured Architecture Decision Record (ADR) in MADR format. Gap M6: no ADRs exist for major OpenClaw architectural choices (MCP-via-mcporter, Carbon frozen, Baileys, dual iMessage path). Returns: ADR markdown, suggested commit path and git command.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `adr_id` | string | — | Optional ADR ID (e.g. 'ADR-0001'). Auto-generated if omitted. |
| `alternatives` | array | ✅ | Alternatives considered. |
| `consequences` | array | ✅ | Positive and negative consequences. |
| `context` | string | ✅ | Problem context and forces. |
| `decision` | string | ✅ | The decision made. |
| `status` | string | — | ADR status. Default: 'proposed'. |
| `title` | string | ✅ | Short decision title. |

### `openclaw_channel_audit`

Detects channel SDK packages present in package.json but absent from README (zombie dependencies). Gap M1: @line/bot-sdk is in deps but LINE has zero documentation — a maintenance liability for 75M+ users in JP/TH. Returns: zombie deps, channel coverage matrix.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `package_json_path` | string | ✅ | Path to package.json. |
| `readme_path` | string | ✅ | Path to README.md. |

### `openclaw_doc_sync_check`

Compares dependency versions in package.json against versions referenced in markdown docs. Gap M5: docs.acp.md says ACP SDK '0.13.x' but package.json has '0.14.1'. Returns: desynced dependencies, severity (HIGH for ACP SDK/Carbon), update instructions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `docs_glob` | string | — | Glob for markdown files to scan. Default: '**/*.md'. |
| `package_json_path` | string | ✅ | Path to package.json. |

### `openclaw_gateway_probe`

Tests Gateway WebSocket connectivity with exponential backoff reconnection. Gaps H6+H7: Gateway unreachable after macOS sleep/wake, LaunchAgent WS 1006 closure. Returns: connection status, latency, close code, exact launchctl restart command.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `backoff_factor` | number | — | Base seconds between retries (doubles each attempt). Default: 1.0. |
| `check_health_endpoints` | boolean | — | Also probe /health, /healthz, /ready, /readyz HTTP endpoints (2026.3.1). Default: true. |
| `gateway_url` | string | — | Gateway WebSocket URL. Default: ws://127.0.0.1:18789. |
| `max_retries` | integer | — | Number of reconnection attempts (1-5). Default: 3. |

---

## security

### `openclaw_credentials_check`

Checks the integrity and freshness of OpenClaw channel credentials. Gap M3: Baileys WhatsApp creds.json can silently corrupt, preventing reconnection. Validates JSON integrity (CRITICAL if corrupted) and staleness (MEDIUM if > max_age_days). Returns: per-credentials-dir findings with severity.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credentials_dir` | string | — | Path to credentials directory. Defaults to ~/.openclaw/credentials. |
| `max_age_days` | integer | — | Max age in days before a credential file is considered stale. Default: 30. |

### `openclaw_gateway_auth_check`

Checks the OpenClaw Gateway authentication configuration. Gap H2: Funnel mode without password auth is a CRITICAL exposure — anyone on the internet can reach the Gateway without authentication. Also detects dangerouslyDisableDeviceAuth=true (HIGH). Returns: findings list with severity and remediation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Absolute path to openclaw.json. Defaults to ~/.openclaw/openclaw.json. |

### `openclaw_log_config_check`

Audits the OpenClaw logging configuration. Gap M7: debug/trace logging leaks tokens and PII into log files. Missing redactPatterns means secrets appear in plain text. Returns: findings with severity HIGH (verbose level) or MEDIUM (missing redact patterns).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Absolute path to openclaw.json. Defaults to ~/.openclaw/openclaw.json. |

### `openclaw_rate_limit_check`

Checks if a rate limiter is configured in front of the OpenClaw Gateway. Gap H8: no rate limiting means Tailscale Funnel exposure creates amplification risk. Returns: funnel status, rate limiter detected?, Nginx/Caddy fix snippets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_funnel` | boolean | — | If true, checks whether Tailscale Funnel mode is active. Default: true. |
| `gateway_config_path` | string | ✅ | Path to OpenClaw config file. |

### `openclaw_sandbox_audit`

Audits the OpenClaw config for sandbox.mode setting. CRITICAL gap C2: sandbox defaults to 'off', giving any agent session full host shell access. A prompt injection → RCE with mode:off. Returns: severity, current mode, fix snippet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | ✅ | Absolute path to the OpenClaw config file (YAML or JSON). |

### `openclaw_security_scan`

Scans source files for SQL injection patterns and dangerous query constructs. Specifically targets the /api/metrics/database vulnerability (openclaw issue #29951). Returns: vulnerabilities with file/line/severity, CVSS-style severity classification, and ready-to-apply remediation snippets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | string | — | Optional endpoint name to highlight (e.g. '/api/metrics/database'). |
| `scan_depth` | integer | — | Maximum directory recursion depth (1-5). Default: 3. |
| `target_path` | string | ✅ | Absolute path to file or directory to scan. |

### `openclaw_session_config_check`

Checks if the express-session secret is configured as a persistent env var. Gap C3: OpenClaw regenerates the session secret on every container restart, causing infinite login loops in rolling/crash deployments (issue #29955). Returns: severity, secret found?, Docker and .env fix snippets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `compose_file_path` | string | — | Path to docker-compose.yml to check (optional). |
| `env_file_path` | string | — | Path to .env file to check (optional). |

### `openclaw_webhook_sig_check`

Checks that each inbound webhook channel has a signing secret configured. Gap M4: Without HMAC signature verification, anyone can forge inbound webhook events, potentially injecting malicious instructions to agents. Checks Telegram, Discord, Slack, MS Teams, Gmail. Returns: findings list with severity HIGH for any channel with webhook but no secret.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | — | Optional: check only this channel (telegram, discord, slack, msteams, gmail). |
| `config_path` | string | — | Absolute path to openclaw.json. Defaults to ~/.openclaw/openclaw.json. |

### `openclaw_workspace_integrity_check`

Validates the integrity of the OpenClaw workspace directory (~/.openclaw/workspace). Gap M8: Missing AGENTS.md / SOUL.md means agents have no identity or instructions. Stale MEMORY.md blocks context continuity. Large files cause agent context bloat. Returns: file inventory, fingerprint, and findings with severity.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stale_days` | integer | — | Days before MEMORY.md is considered stale. Default: 30. |
| `workspace_dir` | string | — | Path to workspace directory. Defaults to ~/.openclaw/workspace. |

---

## spec_compliance

### `openclaw_audio_content_audit`

Audit MCP audio content support (2025-06-18+). Checks mimeType allowlist, size limits, duration limits, and base64 encoding configuration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_elicitation_audit`

Audit MCP elicitation capability compliance (2025-06-18+). Checks capability declaration, requestedSchema validity, URL mode support (2025-11-25), and schema type restrictions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_icon_metadata_audit`

Audit icon metadata support (MCP 2025-11-25). Checks tools/resources/prompts for icon fields, validates icon URLs use HTTPS or data: URI.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_json_schema_dialect_check`

Audit JSON Schema dialect compliance (MCP 2025-11-25). Checks $schema declaration, detects draft-07 only keywords (definitions, dependencies, additionalItems).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_resources_prompts_audit`

Audit MCP Resources & Prompts capability compliance. Checks capability declarations, listChanged support, resource URI schemes, and prompt field completeness.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_sse_transport_audit`

Audit Streamable HTTP / SSE transport compliance (MCP 2025-11-25). Checks transport type, polling support, event ID encoding, Origin validation, MCP-Protocol-Version header.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

### `openclaw_tasks_audit`

Audit MCP Tasks capability compliance (2025-11-25 experimental). Checks tasks declaration, polling interval, timeout config, max concurrent tasks, deferred result retrieval.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Path to openclaw.json config file |

---

## uncategorized

### `openclaw_channel_auth_canon_check`

C8 — Vérifie la canonicalisation des chemins auth pour les channel plugins. Détecte les encoded dot-segment traversal (%2e%2e) qui peuvent contourner la gateway auth sur /api/channels. (Fix 2026.2.26)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_config_include_check`

H13 — Vérifie les guardrails $include dans la config. Détecte les hardlinks, les fichiers oversized, et les targets hors de la racine config. (Fix 2026.2.26 + 2026.2.17)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_config_prototype_check`

H14 — Détecte les clés de prototype pollution (__proto__, constructor, prototype) dans openclaw.json. Bloquées dans config merge/patch depuis 2026.2.22.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_dm_allowlist_check`

M16 — Vérifie que dmPolicy=allowlist avec allowFrom vide est détecté (fail-closed non appliqué). Vérifie tous les canaux : telegram, whatsapp, signal, imessage, discord, slack, line, matrix, feishu. (Fix 2026.2.26)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_exec_approval_freeze_check`

C9 — Vérifie l'immutabilité des plans d'exécution (argv/cwd/agentId/sessionKey). Détecte les shell-wrapper allow-always patterns et les configs sans sandboxing. (Fix 2026.2.26 + 2026.2.22)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_group_policy_default_check`

H16 — Vérifie que le group policy par défaut est fail-closed (allowlist). Détecte les canaux sans groupPolicy explicite. (Fix 2026.2.22)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_hook_session_routing_check`

H12 — Vérifie le durcissement du routing session-key pour les hooks. Détecte allowRequestSessionKey sans prefix gates et les hooks sans token auth. (Breaking 2026.2.12)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_http_headers_check`

H9 — Vérifie la présence des HTTP security headers dans la config gateway (HSTS, X-Content-Type-Options, Referrer-Policy). Ajoutés dans OpenClaw 2026.2.23 / 2026.2.20.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_node_version_check`

C5 — Vérifie que Node.js ≥ 22.12.0 est installé (CVE-2025-59466 async_hooks DoS + CVE-2026-21636 Permission model bypass). Détecte les versions insuffisantes avec guidance de mise à jour.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `node_binary` | string | — | Chemin vers le binaire node (default: auto-detect via PATH) |

### `openclaw_nodes_commands_check`

H10 — Détecte les overrides dangereux de gateway.nodes.allowCommands. Remplace le finding `gateway.nodes.allow_commands_dangerous` de `openclaw security audit` (severity CRITICAL si gateway exposé).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_otel_redaction_check`

M17 — Vérifie la rédaction des secrets dans l'export OTEL/diagnostics. Détecte les credentials inline dans endpoints, headers et span attributes. (Fix 2026.2.27)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_plugin_integrity_check`

H18 — Vérifie l'intégrité et le pin des plugins installés. Détecte les versions non pinnées, les hash manquants, et les drifts post-install. (Plugin integrity tracking 2026.2.26+)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_rpc_rate_limit_check`

M21 — Vérifie la configuration du rate limiting pour le control-plane RPC. Détecte l'absence de rate limit sur les déploiements remote et les webhooks sans throttling.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_safe_bins_profile_check`

H15 — Vérifie que les safeBins ont des profils explicites dans safeBinProfiles. Détecte les interpréteurs sans restriction. (Fix 2026.2.22)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_secrets_lifecycle_check`

C7 — Vérifie le lifecycle complet du workflow External Secrets (audit/configure/apply/reload). Détecte les inline credentials, les snapshots non activées, et la migration incomplète. (2026.2.26+)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json (default: ~/.openclaw/openclaw.json) |

### `openclaw_secrets_workflow_check`

C6 — Détecte les secrets hardcodés dans openclaw.json (tokens, API keys, passwords). Guide la migration vers `openclaw secrets` workflow (External Secrets Management, 2026.2.26+).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json (default: ~/.openclaw/openclaw.json) |

### `openclaw_session_disk_budget_check`

M15 — Vérifie que session.maintenance.maxDiskBytes et highWaterBytes sont configurés pour éviter la croissance illimitée des transcripts. Fonctionnalité ajoutée dans OpenClaw 2026.2.23.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_shell_env_check`

H17 — Vérifie l'assainissement des variables d'environnement shell. Détecte LD_PRELOAD / DYLD_LIBRARY_PATH dans les configs agents, exec et hooks. (Fix 2026.2.22 + Breaking 2026.2.12)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json (default: ~/.openclaw/openclaw.json) |

### `openclaw_token_separation_check`

H19 — Vérifie que hooks.token ≠ gateway.auth.token. La réutilisation de token entre webhook et gateway élargit la surface d'attaque. (Security best practice)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

### `openclaw_trusted_proxy_check`

H11 — Vérifie la cohérence de la config trusted-proxy (auth.mode, bind, trustedProxies, real_ip_fallback_enabled). Détecte les combinaisons invalides corrigées en 2026.2.22 / 2026.2.13.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_path` | string | — | Chemin vers openclaw.json |

---

## vs_bridge

### `vs_context_pull`

Pull the OpenClaw session context (model, tokens, last message, workspace) back into VS Code. Enables Copilot agents to know what OpenClaw has been doing.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | — | Source OpenClaw session (default: main) |
| `workspace_path` | string | — | Filter to linked workspace |

### `vs_context_push`

Push the current VS Code workspace context (open files, active file, recent changes, last agent action) into an OpenClaw session so the OpenClaw agent can reference it. This is the first VS Code ↔ OpenClaw bridge in the ecosystem.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_file` | string | — | Currently focused file |
| `agent_last_action` | string | — | Last Copilot agent action |
| `agent_last_result` | string | — | Output of last agent action |
| `open_files` | array | — | Currently open files |
| `recent_changes` | array | — | Recent file change events |
| `session_id` | string | — | Target OpenClaw session (default: main) |
| `workspace_path` | string | ✅ | Absolute workspace root path |

### `vs_session_link`

Associate a VS Code workspace with a specific OpenClaw session. Once linked, push/pull calls use this session automatically.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | ✅ | — |
| `workspace_path` | string | ✅ | — |

### `vs_session_status`

Return bridge status: linked sessions and gateway reachability.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_path` | string | — | Filter to specific workspace |

---

## workflow_automation

### `openclaw_n8n_workflow_export`

Export an OpenClaw agent pipeline as an n8n-compatible workflow JSON. Converts pipeline steps (name, type, parameters, depends_on) to n8n format with proper node layout and connections. Gap T8: workflow automation bridge.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `output_path` | string | — | Optional file path to write the workflow JSON. |
| `pipeline_name` | string | ✅ | Name for the n8n workflow. |
| `steps` | array | ✅ | List of pipeline steps. Each: {name, type, parameters?, depends_on?}. |

### `openclaw_n8n_workflow_import`

Validate and import an n8n workflow JSON file. Checks structure (nodes, connections, required fields), detects credential references, and optionally copies to workspace. Gap T8: workflow automation bridge.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strict` | boolean | — | Reject workflows with validation issues. Default: true. |
| `target_dir` | string | — | Optional directory to copy the validated workflow into. |
| `workflow_path` | string | ✅ | Path to the n8n workflow JSON file. |

