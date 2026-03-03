# Tool Summary — v3.3.0

138 tools across 26 categories.

| Tool | Category | Description |
|------|----------|-------------|
| `acp_session_list_active` | acp | Lists all persisted ACP sessions with their age and status (active/stale). |
| `acp_session_persist` | acp | Persists an ACP run_id → gateway_session_key mapping to disk. Gap C4: ACP bri... |
| `acp_session_restore` | acp | Reloads ACP sessions from disk after a bridge crash or restart. Purges stale ... |
| `firm_adr_generate` | reliability | Generates a structured Architecture Decision Record (ADR) in MADR format. Gap... |
| `firm_export_auto` | export | Auto-route firm workflow output to the correct export target (GitHub PR, Jira... |
| `firm_export_document` | export | Write firm workflow output to a local Markdown document. |
| `firm_export_github_pr` | export | Create a GitHub draft PR from firm workflow output. Always adds needs-review ... |
| `firm_export_jira_ticket` | export | Create a Jira issue from firm workflow output. |
| `firm_export_linear_issue` | export | Create a Linear issue from firm workflow output. |
| `firm_export_slack_digest` | export | Post a formatted firm delivery digest to Slack via webhook. |
| `firm_gateway_fleet_add` | fleet | Register a new OpenClaw Gateway instance in the fleet. Verifies connectivity ... |
| `firm_gateway_fleet_broadcast` | fleet | Broadcast a message to all (or filtered) Gateway instances. Useful for fleet-... |
| `firm_gateway_fleet_list` | fleet | List all registered Gateway instances with their configuration. |
| `firm_gateway_fleet_remove` | fleet | Remove a Gateway instance from the fleet registry. |
| `firm_gateway_fleet_status` | fleet | Health check all registered OpenClaw Gateway instances. Runs parallel /health... |
| `firm_gateway_fleet_sync` | fleet | Sync configuration or skills across all fleet instances in parallel. |
| `fleet_cron_schedule` | acp | Schedules a cron task on the main session, bypassing sandbox denylist. Gap H4... |
| `fleet_session_inject_env` | acp | Broadcasts provider env vars (API keys, model config) to all non-main Gateway... |
| `openclaw_a2a_cancel_task` | a2a | Cancel a running A2A task (RC v1.0 CancelTask). Error if task is in terminal ... |
| `openclaw_a2a_card_generate` | a2a | Generate .well-known/agent-card.json from a SOUL.md file. RC v1.0 compliant w... |
| `openclaw_a2a_card_validate` | a2a | Validate an A2A Agent Card against RC v1.0 spec. Detects deprecated v0.4.0 pa... |
| `openclaw_a2a_discovery` | a2a | Discover agents via Agent Cards or local SOUL.md scan (RC v1.0). Probes .well... |
| `openclaw_a2a_push_config` | a2a | CRUD for push notification webhooks (RC v1.0). Create/Get/List/Delete push co... |
| `openclaw_a2a_subscribe_task` | a2a | Subscribe to task updates via SSE (RC v1.0 SubscribeToTask). Streams TaskStat... |
| `openclaw_a2a_task_send` | a2a | Send a message/task to an A2A agent (RC v1.0 SendMessage). Typed parts (TextP... |
| `openclaw_a2a_task_status` | a2a | Get task status (GetTask) or list tasks (ListTasks). RC v1.0 with contextId f... |
| `openclaw_acpx_version_check` | acp | Checks ACPX plugin version pin (>= 0.1.15) and streaming mode (final_only). 2... |
| `openclaw_adaptive_thinking_check` | platform | Checks Claude 4.6 model configs for correct adaptive thinking defaults (2026.... |
| `openclaw_agent_identity_audit` | compliance_medium | Audit agent decentralized identity (DID) — format, verification methods, sign... |
| `openclaw_agent_routing_check` | platform | Validate agent routing bindings (2026.2.26+). Checks default route, scope iso... |
| `openclaw_agent_team_orchestrate` | orchestration | Execute a task DAG across the agent fleet with parallel layer execution, depe... |
| `openclaw_agent_team_status` | orchestration | Check status of running or completed fleet orchestrations. Returns task progr... |
| `openclaw_audio_content_audit` | spec_compliance | Audit MCP audio content support (2025-06-18+). Checks mimeType allowlist, siz... |
| `openclaw_autoupdate_check` | platform | Self-update supply chain integrity check (2026.2.22+). Checks update channel,... |
| `openclaw_browser_context_check` | browser_automation | Validates Playwright/Puppeteer headless browser configuration for agent use. ... |
| `openclaw_channel_audit` | reliability | Detects channel SDK packages present in package.json but absent from README (... |
| `openclaw_channel_auth_canon_check` | — | C8 — Vérifie la canonicalisation des chemins auth pour les channel plugins. D... |
| `openclaw_ci_pipeline_check` | observability | Validates CI workflow completeness: checks that .github/workflows/ contains l... |
| `openclaw_circuit_breaker_audit` | compliance_medium | Audit circuit breaker / resilience configuration for external calls — timeout... |
| `openclaw_config_include_check` | — | H13 — Vérifie les guardrails $include dans la config. Détecte les hardlinks, ... |
| `openclaw_config_prototype_check` | — | H14 — Détecte les clés de prototype pollution (__proto__, constructor, protot... |
| `openclaw_content_boundary_check` | platform | Content boundary & anti-prompt-injection audit (2026.2+). Checks wrapExternal... |
| `openclaw_context_health_check` | ecosystem | Context rot / cognitive health detection. Checks token utilization, session a... |
| `openclaw_cost_analytics` | ecosystem | Usage/cost tracking and analysis. Estimates cost per session, checks budget t... |
| `openclaw_credentials_check` | security | Checks the integrity and freshness of OpenClaw channel credentials. Gap M3: B... |
| `openclaw_dm_allowlist_check` | — | M16 — Vérifie que dmPolicy=allowlist avec allowFrom vide est détecté (fail-cl... |
| `openclaw_doc_sync_check` | reliability | Compares dependency versions in package.json against versions referenced in m... |
| `openclaw_elicitation_audit` | spec_compliance | Audit MCP elicitation capability compliance (2025-06-18+). Checks capability ... |
| `openclaw_exec_approval_freeze_check` | — | C9 — Vérifie l'immutabilité des plans d'exécution (argv/cwd/agentId/sessionKe... |
| `openclaw_gateway_auth_check` | security | Checks the OpenClaw Gateway authentication configuration. Gap H2: Funnel mode... |
| `openclaw_gateway_probe` | reliability | Tests Gateway WebSocket connectivity with exponential backoff reconnection. G... |
| `openclaw_gdpr_residency_audit` | compliance_medium | Audit GDPR compliance and data residency — legal basis, retention, PII fields... |
| `openclaw_group_policy_default_check` | — | H16 — Vérifie que le group policy par défaut est fail-closed (allowlist). Dét... |
| `openclaw_hebbian_analyze` | hebbian_memory | Analyze co-activation patterns from harvested sessions. Uses Jaccard similari... |
| `openclaw_hebbian_decay_config_check` | hebbian_memory | Validate Hebbian parameters: learning_rate, decay, poids_min/max, consolidati... |
| `openclaw_hebbian_drift_check` | hebbian_memory | Detect Claude.md semantic drift vs a baseline using TF-IDF cosine similarity.... |
| `openclaw_hebbian_harvest` | hebbian_memory | Ingest JSONL session logs into the local Hebbian SQLite database. PII/secrets... |
| `openclaw_hebbian_layer_validate` | hebbian_memory | Validate the 4-layer structure of a Hebbian-augmented Claude.md: CORE (L1), C... |
| `openclaw_hebbian_pii_check` | hebbian_memory | Audit PII stripping configuration: regex patterns (email, phone, IP, API keys... |
| `openclaw_hebbian_status` | hebbian_memory | Dashboard: total sessions, Layer 2 rule weights, atrophy/promotion candidates... |
| `openclaw_hebbian_weight_update` | hebbian_memory | Compute or apply Hebbian weight updates on Layer 2 rules in Claude.md. Uses t... |
| `openclaw_hook_session_routing_check` | — | H12 — Vérifie le durcissement du routing session-key pour les hooks. Détecte ... |
| `openclaw_http_headers_check` | — | H9 — Vérifie la présence des HTTP security headers dans la config gateway (HS... |
| `openclaw_i18n_audit` | i18n | Audits internationalization files for missing keys, empty values, interpolati... |
| `openclaw_icon_metadata_audit` | spec_compliance | Audit icon metadata support (MCP 2025-11-25). Checks tools/resources/prompts ... |
| `openclaw_json_schema_dialect_check` | spec_compliance | Audit JSON Schema dialect compliance (MCP 2025-11-25). Checks $schema declara... |
| `openclaw_knowledge_graph_check` | memory | Audits knowledge graph integrity: backend validation, TTL policy, orphan node... |
| `openclaw_legal_creation_checklist` | legal_status | Post-creation compliance checklist — steps, costs, timeline, and annual oblig... |
| `openclaw_legal_governance_audit` | legal_status | Governance structure audit — recommends statutory clauses, pactes d'associés,... |
| `openclaw_legal_social_protection` | legal_status | Social protection analysis by status — TNS vs assimilé salarié vs micro-entre... |
| `openclaw_legal_status_compare` | legal_status | Compare legal forms (SAS, SARL, SASU, EURL, etc.) with multi-criteria scoring... |
| `openclaw_legal_tax_simulate` | legal_status | Tax simulation IS vs IR over 3-5 years. Includes salary/dividend optimization... |
| `openclaw_location_geo_analysis` | location_strategy | Geo-economic analysis of candidate cities — talent pools, transport, ecosyste... |
| `openclaw_location_incentives` | location_strategy | Tax incentives and aid programs by territory — ZFU, ZRR, BER, CIR, JEI, BPI, ... |
| `openclaw_location_real_estate` | location_strategy | Real estate market intelligence — availability, pricing per sqm, coworking ra... |
| `openclaw_location_site_score` | location_strategy | Multi-criteria site scoring with 20+ weighted criteria. Compares sites on tra... |
| `openclaw_location_tco_simulate` | location_strategy | Total Cost of Occupation simulation over 3-5 years. Includes rent, charges, C... |
| `openclaw_log_config_check` | security | Audits the OpenClaw logging configuration. Gap M7: debug/trace logging leaks ... |
| `openclaw_market_competitive_analysis` | market_research | Full competitive landscape analysis. Produces feature matrix, SWOT per compet... |
| `openclaw_market_financial_benchmark` | market_research | Financial benchmarking — unit economics (CAC, LTV, ARPU, churn), pricing anal... |
| `openclaw_market_report_generate` | market_research | Generate a complete professional market research report in Markdown. Structur... |
| `openclaw_market_research_monitor` | market_research | Continuous competitive monitoring. Actions: add/remove competitors, log marke... |
| `openclaw_market_sizing` | market_research | TAM/SAM/SOM market sizing with top-down and bottom-up approaches. Includes gr... |
| `openclaw_market_web_research` | market_research | Structured web research and OSINT intelligence gathering. Multi-source (Crunc... |
| `openclaw_mcp_firewall_check` | ecosystem | MCP Gateway firewall policy audit. Checks tool allowlists, argument sanitizat... |
| `openclaw_model_routing_audit` | compliance_medium | Audit multi-model routing — strategy, fallback chain, cost caps, provider div... |
| `openclaw_n8n_workflow_export` | workflow_automation | Export an OpenClaw agent pipeline as an n8n-compatible workflow JSON. Convert... |
| `openclaw_n8n_workflow_import` | workflow_automation | Validate and import an n8n workflow JSON file. Checks structure (nodes, conne... |
| `openclaw_node_version_check` | — | C5 — Vérifie que Node.js ≥ 22.12.0 est installé (CVE-2025-59466 async_hooks D... |
| `openclaw_nodes_commands_check` | — | H10 — Détecte les overrides dangereux de gateway.nodes.allowCommands. Remplac... |
| `openclaw_oauth_oidc_audit` | auth_compliance | Audit OAuth 2.1 / OIDC Discovery compliance (MCP 2025-06-18 / 2025-11-25). Ch... |
| `openclaw_observability_pipeline` | observability | Ingests JSONL structured logs/traces (OpenTelemetry format) into a local SQLi... |
| `openclaw_otel_redaction_check` | — | M17 — Vérifie la rédaction des secrets dans l'export OTEL/diagnostics. Détect... |
| `openclaw_pgvector_memory_check` | memory | Validates pgvector configuration for semantic memory: index type (HNSW recomm... |
| `openclaw_plugin_integrity_check` | — | H18 — Vérifie l'intégrité et le pin des plugins installés. Détecte les versio... |
| `openclaw_plugin_sdk_check` | platform | Plugin SDK integrity validation (2026.1.16+). Checks plugin hooks, permission... |
| `openclaw_prompt_injection_batch` | prompt_security | Batch scan multiple text inputs for injection patterns. Accepts a list of {id... |
| `openclaw_prompt_injection_check` | prompt_security | Scan text for prompt injection and jailbreak patterns. Detects 16 pattern fam... |
| `openclaw_provenance_tracker` | ecosystem | Cryptographic audit trail / provenance tracking. Actions: append (hash chain ... |
| `openclaw_rag_pipeline_check` | ecosystem | RAG pipeline health & configuration audit. Checks embedding model, vector sto... |
| `openclaw_rate_limit_check` | security | Checks if a rate limiter is configured in front of the OpenClaw Gateway. Gap ... |
| `openclaw_resource_links_audit` | compliance_medium | Audit MCP resource links in tool results — URI validation, MIME types, subscr... |
| `openclaw_resources_prompts_audit` | spec_compliance | Audit MCP Resources & Prompts capability compliance. Checks capability declar... |
| `openclaw_rpc_rate_limit_check` | — | M21 — Vérifie la configuration du rate limiting pour le control-plane RPC. Dé... |
| `openclaw_safe_bins_profile_check` | — | H15 — Vérifie que les safeBins ont des profils explicites dans safeBinProfile... |
| `openclaw_sandbox_audit` | security | Audits the OpenClaw config for sandbox.mode setting. CRITICAL gap C2: sandbox... |
| `openclaw_sandbox_exec_check` | ecosystem | Sandbox execution isolation audit. Checks sandbox mode, resource limits, file... |
| `openclaw_secrets_lifecycle_check` | — | C7 — Vérifie le lifecycle complet du workflow External Secrets (audit/configu... |
| `openclaw_secrets_v2_audit` | platform | Audit the OpenClaw secrets v2 lifecycle (2026.2.26+). Checks external provide... |
| `openclaw_secrets_workflow_check` | — | C6 — Détecte les secrets hardcodés dans openclaw.json (tokens, API keys, pass... |
| `openclaw_security_scan` | security | Scans source files for SQL injection patterns and dangerous query constructs.... |
| `openclaw_session_config_check` | security | Checks if the express-session secret is configured as a persistent env var. G... |
| `openclaw_session_disk_budget_check` | — | M15 — Vérifie que session.maintenance.maxDiskBytes et highWaterBytes sont con... |
| `openclaw_shell_env_check` | — | H17 — Vérifie l'assainissement des variables d'environnement shell. Détecte L... |
| `openclaw_skill_lazy_loader` | performance | Lazy-loads SKILL.md metadata (YAML front-matter) without parsing full content... |
| `openclaw_skill_search` | performance | Search skills by keyword/tags across all SKILL.md files. Returns relevance-ra... |
| `openclaw_sqlite_vec_check` | platform | SQLite-vec memory backend validation (2026.1.12+). Checks backend config, db ... |
| `openclaw_sse_transport_audit` | spec_compliance | Audit Streamable HTTP / SSE transport compliance (MCP 2025-11-25). Checks tra... |
| `openclaw_supplier_contract_check` | procurement | Contract clause analysis — checks SLA, penalties, data protection (DPA), reve... |
| `openclaw_supplier_evaluate` | procurement | Multi-criteria supplier evaluation with 15+ weighted criteria. Scores quality... |
| `openclaw_supplier_risk_monitor` | procurement | Continuous supplier risk monitoring — add/remove/update/status/export watchli... |
| `openclaw_supplier_search` | procurement | Market-wide supplier sourcing — identifies potential suppliers by category, b... |
| `openclaw_supplier_tco_analyze` | procurement | Total Cost of Ownership analysis over 3-5 years. Includes license, integratio... |
| `openclaw_tasks_audit` | spec_compliance | Audit MCP Tasks capability compliance (2025-11-25 experimental). Checks tasks... |
| `openclaw_token_budget_optimizer` | ecosystem | Token optimization analysis. Finds compression opportunities, prompt deduplic... |
| `openclaw_token_scope_check` | auth_compliance | Check if OAuth scopes properly restrict tool access. Verifies each tool has s... |
| `openclaw_token_separation_check` | — | H19 — Vérifie que hooks.token ≠ gateway.auth.token. La réutilisation de token... |
| `openclaw_tool_deprecation_audit` | compliance_medium | Audit tool deprecation lifecycle — sunset dates, replacements, circular chains. |
| `openclaw_trust_model_check` | platform | Validate trust model and multi-user heuristics (2026.2.24+). Checks multi-use... |
| `openclaw_trusted_proxy_check` | — | H11 — Vérifie la cohérence de la config trusted-proxy (auth.mode, bind, trust... |
| `openclaw_voice_security_check` | platform | TTS/voice channel security audit (2026.2.24+). Checks provider auth, rate lim... |
| `openclaw_webhook_sig_check` | security | Checks that each inbound webhook channel has a signing secret configured. Gap... |
| `openclaw_workspace_integrity_check` | security | Validates the integrity of the OpenClaw workspace directory (~/.openclaw/work... |
| `openclaw_workspace_lock` | acp | Advisory file lock with timeout and owner tracking. Gap H5: race condition in... |
| `vs_context_pull` | vs_bridge | Pull the OpenClaw session context (model, tokens, last message, workspace) ba... |
| `vs_context_push` | vs_bridge | Push the current VS Code workspace context (open files, active file, recent c... |
| `vs_session_link` | vs_bridge | Associate a VS Code workspace with a specific OpenClaw session. Once linked, ... |
| `vs_session_status` | vs_bridge | Return bridge status: linked sessions and gateway reachability. |
