# CLAUDE.md — setup-vs-agent-firm

> Ce fichier est lu automatiquement par Claude Code à chaque session.
> Il définit les **règles non-négociables**, les **workflows obligatoires** et les
> **bonnes pratiques Anthropic** à appliquer sur **chaque tâche**, sans exception.

---

## ⚠️ RÈGLES OBLIGATOIRES — TOUTES LES TÂCHES

Ces règles s'appliquent **avant de commencer** n'importe quelle tâche, petite ou grande.

### 1. Git propre avant de commencer
```bash
git status          # aucun fichier non commité
git checkout -b feat/<slug>   # nouvelle branche dédiée
```
Commite des checkpoints réguliers (`git commit` toutes les 30-50 lignes de code généré).
Ne jamais travailler directement sur `main`.

### 2. Pydantic sur tous les inputs
- Tout nouveau tool MCP → classe `BaseModel` dans `src/models.py` + entrée dans `TOOL_MODELS`
- Tout script avec des arguments CLI → validation via Pydantic ou argparse strict
- Contraintes minimales obligatoires : `min_length`, `max_length`, regex sur les slugs/noms,
  blocage du path traversal (`..`) sur tous les chemins de fichiers

### 3. Tests avant le push
- Toute nouvelle fonction ou tool → au moins 1 test positif + 1 test négatif (input invalide)
- `python -m pytest tests/ -v` doit passer à **100 %** avant chaque `git push`
- Coverage minimum : **80 %** (lignes + branches + fonctions) — pas de merge sous ce seuil
- En cas d'échec de test : corriger le code, pas l'assertion (sauf si l'assertion est fausse)

### 4. Secrets masqués, jamais loggés
- Aucun token, API key, ou mot de passe dans les logs, commits, ou outputs
- Utiliser `_mask_secret(val)` (4 derniers caractères visibles) pour tout affichage
- `.env` toujours dans `.gitignore`

### 5. Outputs AI marqués
Tout deliverable généré par un agent doit porter :
```
⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
```

### 6. Pas de code inline dans le terminal
- Ne **jamais** exécuter plus de ~10 lignes de code directement dans le terminal (`python -c`, heredoc, etc.)
- Au-delà de 10 lignes : écrire un script temporaire (`/tmp/script.py`) puis le lancer
- Raison : le shell multi-ligne casse le quoting, bloque sur les `"`, et produit des commandes irrécupérables
- Idem pour les commit messages multi-lignes : utiliser `git commit -F /tmp/msg.txt`

---

## 🏗️ WORKFLOWS ANTHROPIC — PRATIQUES DES ÉQUIPES INTERNES

Pratiques tirées du document officiel **"How Anthropic teams use Claude Code"**
(interviews des équipes Data Infrastructure, Product, Security, Design, Legal).

### Mode auto-accept pour le prototypage
- Activer `shift+tab` (auto-accept) pour les tâches de prototypage ≤ 2h
- Laisser Claude itérer : écrire le code → lancer les tests → corriger → recommencer
- Partir d'un état git **propre** ; commiter des checkpoints toutes les 30 min
- Reviewer la solution à ~80 % d'avancement, puis prendre la main pour les 20 % finaux

### Instances parallèles pour les tâches longues
- Ouvrir plusieurs instances Claude Code dans des repositories différents simultanément
- Chaque instance maintient son contexte complet — pas de perte de contexte
- Utiliser `firm_gateway_fleet_broadcast` pour synchroniser les résultats entre instances

### Prompts en langage naturel pour les non-développeurs
- Accepter des fichiers texte décrivant un workflow en langage naturel
- Extraire les inputs nécessaires (dates, paramètres) et les demander explicitement
- Produire un output exploitable (Excel, Markdown, PR, ticket) sans intervention manuelle

### Débogage par screenshots / stack traces
- Accepter des captures d'écran de dashboards ou des stack traces en entrée
- Tracer le flux de contrôle dans le codebase avant de proposer un fix
- Fournir les commandes exactes à exécuter, pas seulement le diagnostic

### Onboarding et navigation dans la codebase
- Lire `CLAUDE.md`, `AGENTS.md`, `README.md` en priorité absolue sur chaque session
- Identifier les fichiers pertinents pour la tâche courante avant d'éditer quoi que ce soit
- Expliquer les dépendances des pipelines si demandé (remplace les catalogues de données)

### Documentation de fin de session
Après chaque session de travail significative :
1. Résumer ce qui a été accompli (1 paragraph)
2. Lister les décisions d'architecture prises
3. Proposer des améliorations à ajouter à ce `CLAUDE.md`
4. Commiter le `CLAUDE.md` mis à jour si des améliorations sont validées

### Tests & GitHub Actions
- Utiliser Claude Code pour écrire les tests **après** l'implémentation d'une feature
- Adresser automatiquement les commentaires de PR (formatage, renommage) via GitHub Actions
- Le workflow `.github/workflows/openclaw-review.yml` tourne sur chaque PR — ne pas le bypasser

---

## 🏢 STRUCTURE DU PROJET

```
setup-vs-agent-firm/
├── CLAUDE.md                        ← ce fichier (lire en premier)
├── README.md                        ← guide d'installation complet
├── factory/
│   └── generate-firm.sh             ← générateur de firms (15 secteurs, 3 tailles)
├── skills/                          ← SKILL.md publiables sur ClawHub
│   ├── firm-orchestration/          ← A2A protocol (gap #1)
│   ├── firm-{legal,medtech,ecommerce,fintech,saas}-pack/  ← sector packs (gap #2)
│   ├── firm-delivery-export/        ← pipeline delivrables (gap #6)
│   ├── firm-security-audit/         ← séquence audit 5 étapes + remediations (C1,C2,C3,H8)
│   ├── firm-acp-bridge/             ← protocoles ACP persistence + cron + locking (C4,H3,H4,H5)
│   ├── firm-hebbian-memory/         ← mémoire adaptative hebbienne (CDC v1.0.0)
│   └── firm-a2a-bridge/             ← A2A Protocol v1.0 RC bridge (6 tools)
├── souls/                           ← 5 SOUL.md (CEO, CFO, CTO, Legal, HR)
├── .github/workflows/
│   └── openclaw-review.yml          ← Quality dept review on every PR
└── mcp-openclaw-extensions/         ← repo séparé (git submodule optionnel)
    ├── src/
    │   ├── security_audit.py        ← 4 tools sécurité (C1,C2,C3,H8)
    │   ├── acp_bridge.py            ← 6 tools ACP + fleet (C4,H3,H4,H5)
    │   ├── reliability_probe.py     ← 4 tools fiabilité + ADR (H6,H7,M1,M5,M6)
    │   ├── gateway_hardening.py     ← 5 tools Gateway auth + credentials + webhooks (H2,M3,M4,M7,M8)
    │   ├── runtime_audit.py         ← 7 tools runtime & config (C5,C6,H9,H10,H11,M15,M16)
    │   ├── advanced_security.py     ← 8 tools sécurité avancée (C7,C8,C9,H12,H13,H14,H15,H16)
    │   ├── config_migration.py      ← 5 tools migration config (H17,H18,H19,M17,M21)
    │   ├── observability.py         ← 2 tools observabilité (T1,T6)
    │   ├── memory_audit.py          ← 2 tools mémoire (T3,T9)
    │   ├── agent_orchestration.py   ← 2 tools orchestration (T4)
    │   ├── i18n_audit.py            ← 1 tool i18n (T5)
    │   ├── skill_loader.py          ← 2 tools skill loading (T7)
    │   ├── n8n_bridge.py            ← 2 tools n8n workflow bridge (T8)
    │   ├── browser_audit.py         ← 1 tool browser automation (T10)
    │   ├── hebbian_memory.py        ← 8 tools mémoire hebbienne (CDC §3-5)
    │   ├── a2a_bridge.py            ← 6 tools A2A Protocol v1.0 RC (G1-G6)
    │   ├── platform_audit.py        ← 8 tools platform alignment 2026.2 (G7-G14)
    │   ├── ecosystem_audit.py       ← 7 tools ecosystem differentiation (G15-G21)
    │   ├── models.py                ← 96 modèles Pydantic + TOOL_MODELS + cross-field validators
    │   └── main.py                  ← 21 modules, 96 tools enregistrés, v2.0.0
    └── tests/
        └── test_smoke.py            ← 264 tests, 100% pass
```

---

## 🔧 OUTILS DISPONIBLES (MCP server port 8012)

| Catégorie | Tools | Usage typique |
|-----------|-------|---------------|
| VS Bridge | `vs_context_push/pull`, `vs_session_link/status` | Sync contexte VS Code ↔ Gateway |
| Fleet | `firm_gateway_fleet_{status,add,remove,broadcast,sync,list}` | Gérer N instances Gateway |
| Delivery | `firm_export_{github_pr,jira_ticket,linear_issue,slack_digest,document,auto}` | Publier les deliverables |
| Security | `openclaw_security_scan`, `openclaw_sandbox_audit`, `openclaw_session_config_check`, `openclaw_rate_limit_check` | Audit sécurité avant déploiement |
| ACP Bridge | `acp_session_{persist,restore,list_active}`, `fleet_session_inject_env`, `fleet_cron_schedule`, `openclaw_workspace_lock` | Persistence sessions + cron + locking |
| Reliability | `openclaw_gateway_probe`, `openclaw_doc_sync_check`, `openclaw_channel_audit`, `firm_adr_generate` | Fiabilité + ADR + dépendances |
| Gateway Hardening | `openclaw_gateway_auth_check`, `openclaw_credentials_check`, `openclaw_webhook_sig_check`, `openclaw_log_config_check`, `openclaw_workspace_integrity_check` | Auth Gateway + credentials Baileys + webhooks HMAC + logs + workspace |
| Runtime Audit | `openclaw_node_version_check`, `openclaw_secrets_workflow_check`, `openclaw_http_headers_check`, `openclaw_nodes_commands_check`, `openclaw_trusted_proxy_check`, `openclaw_session_disk_budget_check`, `openclaw_dm_allowlist_check` | Node.js version + secrets + headers + nodes.allowCommands + trusted-proxy + disk budget + dmPolicy (C5,C6,H9,H10,H11,M15,M16) |
| Advanced Security | `openclaw_secrets_lifecycle_check`, `openclaw_channel_auth_canon_check`, `openclaw_exec_approval_freeze_check`, `openclaw_hook_session_routing_check`, `openclaw_config_include_check`, `openclaw_config_prototype_check`, `openclaw_safe_bins_profile_check`, `openclaw_group_policy_default_check` | External Secrets lifecycle + path canonicalization + exec plan freeze + hook routing + $include guards + prototype pollution + safeBins profiles + group policy (C7,C8,C9,H12,H13,H14,H15,H16) |
| Config Migration | `openclaw_shell_env_check`, `openclaw_plugin_integrity_check`, `openclaw_token_separation_check`, `openclaw_otel_redaction_check`, `openclaw_rpc_rate_limit_check` | Shell env sanitization + plugin integrity + token separation + OTEL redaction + RPC rate limiting (H17,H18,H19,M17,M21) |
| Observability | `openclaw_observability_pipeline`, `openclaw_ci_pipeline_check` | JSONL→SQLite traces + CI workflow validation (T1,T6) |
| Memory Audit | `openclaw_pgvector_memory_check`, `openclaw_knowledge_graph_check` | pgvector config + knowledge graph integrity (T3,T9) |
| Agent Orchestration | `openclaw_agent_team_orchestrate`, `openclaw_agent_team_status` | Task DAG parallel execution + status (T4) |
| i18n Audit | `openclaw_i18n_audit` | Locale file scanning + missing key detection (T5) |
| Skill Loader | `openclaw_skill_lazy_loader`, `openclaw_skill_search` | Lazy SKILL.md loading + keyword search (T7) |
| n8n Bridge | `openclaw_n8n_workflow_export`, `openclaw_n8n_workflow_import` | n8n workflow export/import (T8) |
| Browser Audit | `openclaw_browser_context_check` | Playwright/Puppeteer headless config validation (T10) |
| Hebbian Memory | `openclaw_hebbian_{harvest,weight_update,analyze,status,layer_validate,pii_check,decay_config_check,drift_check}` | Mémoire adaptative hebbienne : harvest JSONL, poids Layer 2, co-activations, PII stripping, drift detection (CDC §3-5) |
| A2A Bridge | `openclaw_a2a_{card_generate,card_validate,task_send,task_status,push_config,discovery}` | A2A Protocol v1.0 RC — agent cards, task lifecycle, push notifications, discovery (G1-G6) |
| Platform Audit | `openclaw_{secrets_v2_audit,agent_routing_check,voice_security_check,trust_model_check,autoupdate_check,plugin_sdk_check,content_boundary_check,sqlite_vec_check}` | Secrets v2 + routing + voice + trust + autoupdate + plugin SDK + content boundaries + sqlite-vec (G7-G14) |
| Ecosystem Audit | `openclaw_{mcp_firewall_check,rag_pipeline_check,sandbox_exec_check,context_health_check,provenance_tracker,cost_analytics,token_budget_optimizer}` | MCP firewall + RAG + sandbox + context health + provenance + cost + token budget (G15-G21) |

Vérifier que le serveur est actif avant toute tâche impliquant ces tools :
```bash
bash mcp-openclaw-extensions/scripts/status.sh
```

---

## 📋 CHECKLIST DE TÂCHE COMPLÈTE

Avant de marquer une tâche comme terminée, vérifier chaque point :

- [ ] Branche git dédiée créée (`feat/`, `fix/`, `chore/`)
- [ ] Pydantic : modèle de validation créé/mis à jour si nouvel input
- [ ] Tests : `pytest -v` → 100 % pass
- [ ] Secrets : aucun token dans les commits (vérifier avec `git diff --cached`)
- [ ] Output AI marqué avec disclaimer si deliverable externe
- [ ] `CLAUDE.md` mis à jour si nouvelle pratique découverte
- [ ] Commit message clair : `type(scope): description` + liste des changements
- [ ] **Review Pydantic** : vérifier traversal bloqué, defaults cohérents, inputs valides acceptés, `TOOL_MODELS` complet
- [ ] **Tests Pydantic** : script dédié (`/tmp/pydantic_review.py`) exécuté et 100 % pass
- [ ] PR créée en **draft** avec label `needs-review` (seulement après review + tests OK)

---

## � JOURNAL DE SESSION

### Session du 28 février 2026 — Fermeture des gaps OpenClaw (feat/close-openclaw-gaps)

**Accompli :**
Fermeture de 12 gaps OpenClaw (4 CRITICAL, 5 HIGH, 3 MEDIUM) via 3 nouveaux modules Python
(14 tools MCP), 2 nouvelles SKILL.md, et la mise à jour du SOUL CTO + factory. Les 39 tests
passent à 100 %. Branche `feat/close-openclaw-gaps` prête pour review.

**Décisions d'architecture :**
- **JSON file vs Redis/SQLite** pour la persistence ACP : choix JSON avec `os.replace()` atomique
  (zéro dépendance, suffisant pour ≤10k sessions, réversible — cf. `skills/firm-acp-bridge/SKILL.md`)
- **`fcntl.LOCK_EX | LOCK_NB`** pour les race conditions workspace : advisory lock plutôt que
  mutex en mémoire (résiste aux crashes de process)
- **Allowlist stricte** pour `fleet_session_inject_env` : regex `ANTHROPIC_API_KEY|OPENAI_API_KEY|…`
  plus sûre qu'une blocklist (principe de moindre privilege)
- **MADR** choisi comme format ADR : lisible par des non-développeurs, commit-friendly
- **Coverage threshold 80 %** (était 70 %) encodé dans factory + SOUL CTO + ce CLAUDE.md

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet mise à jour (nouveaux fichiers + sous-répos)
- Table outils étendue : 30 tools en 6 catégories (était 3 catégories)
- Règle 3 : seuil coverage porté à 80 %
- Ce journal de session ajouté (section 📓)

---

### Session du 2 mars 2026 — Runtime Audit + 7 nouveaux gaps (feat/close-openclaw-gaps-v2)

**Accompli :**
Audit du CHANGELOG openclaw jusqu'à la version 2026.2.27. Identification et fermeture de 7 nouveaux
gaps (2 CRITICAL, 3 HIGH, 2 MEDIUM) via un nouveau module Python `runtime_audit.py` (7 tools MCP).
Total porté à **42 tools / 8 modules / 69 tests à 100 %**. Branche `feat/close-openclaw-gaps-v2`
prête pour review sur les deux repos.

**Décisions d'architecture :**
- **`subprocess.run([node_bin, "--version"])`** pour C5 : vérification runtime du binaire Node.js
  (pas de parsing de package.json — reflet de la version réellement exécutée)
- **Exclusion des placeholders `$` et `{{`** pour C6 : pattern `$ENV_VAR` et `{{secret}}` indica-
  teurs légitimes de workflows secrets — false-positive rate réduit à ~0
- **HSTS uniquement sur bind non-loopback** pour H9 : HSTS sur loopback = INFO seulement, pas un
  vrai risque de sécurité
- **9 canaux DM vérifiés** pour M16 : telegram, whatsapp, signal, imessage, discord, slack,
  line, matrix, feishu — liste exhaustive des canaux supportés par OpenClaw 2026

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet : `runtime_audit.py` + 42 models + 8 modules + 69 tests
- Table outils : ligne "Runtime Audit" ajoutée (7 tools C5,C6,H9,H10,H11,M15,M16)
- Ce journal de session ajouté

---

### Session du 1er mars 2026 — Gateway Hardening + 6 nouveaux gaps (feat/close-openclaw-gaps)

**Accompli :**
Fermeture de 6 gaps supplémentaires (H2, M3, M4, M7, M8, M9) via un nouveau module Python
`gateway_hardening.py` (5 tools MCP) + génération CONTRIBUTING.md dans la factory. Total porté
à 35 tools, 52 tests à 100 %. Les 5 modèles Pydantic (path-traversal guard + contraintes de type)
respectent la règle obligatoire de ce CLAUDE.md. Les deux READMEs sont mis à jour (35 tools, 26 gaps).

**Décisions d'architecture :**
- **`gateway.controlUi.dangerouslyDisableDeviceAuth`** (pas `gateway.dangerouslyDisableDeviceAuth`) :
  le champ est imbriqué sous `controlUi` dans le schéma OpenClaw — importance de lire les specs avant d'écrire les tests
- **Sévérité CRITICAL** pour Funnel sans password : confirmé dans SECURITY.md openclaw ("Funnel refuses to start unless `gateway.auth.mode: password` is set")
- **JSON file natif** pour éviter les dépendances Redis/SQLite — pattern cohérent avec l'approche ACP bridge
- **CONTRIBUTING.md** généré dans la factory (M9) : template avec labels `good-first-issue`, `ai-assisted`, section sécurité (responsible disclosure), checklist PR pydantic/tests/secrets

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet : `gateway_hardening.py` + 35 models + 7 modules + 52 tests
- Table outils : ligne "Gateway Hardening" ajoutée (5 tools H2,M3,M4,M7,M8)
- Ce journal de session ajouté

---

### Session du 3 mars 2026 — Advanced Security + Config Migration (feat/close-openclaw-gaps-v3)

**Accompli :**
Analyse cross-repo complète (gap analysis) identifiant 19 nouveaux gaps + 20 inefficiences.
Implémentation de 13 gaps (3 CRITICAL, 8 HIGH, 2 MEDIUM) via 2 nouveaux modules Python :
`advanced_security.py` (8 tools) et `config_migration.py` (5 tools). Total porté à
**55 tools / 10 modules / 98 tests à 100 %**. Les 13 modèles Pydantic (path-traversal guard)
respectent les règles. Branche `feat/close-openclaw-gaps-v3` prête pour review.

**Décisions d'architecture :**
- **Recursive `_scan_proto_keys()`** pour H14 : scan profond de toute la config JSON à la recherche
  de `__proto__`, `constructor`, `prototype` — protège contre les objets imbriqués
- **`stat.st_nlink > 1`** pour H13 : détection de hardlinks sur les $include — méthode portable POSIX
- **14 canaux group policy** pour H16 : liste étendue à slack, discord, telegram, whatsapp, signal,
  imessage, line, matrix, mattermost, google-chat, irc, nextcloud-talk, feishu, zalo
- **Interpreter set** pour H15 : python/ruby/perl/node/deno/bun/lua/php/bash/sh/zsh/fish/powershell/pwsh
  — tout binary dans ce set sans profil safeBinProfiles est CRITICAL
- **3 emplacements env** pour H17 : scan agents.defaults.env + tools.exec.env + hooks.env pour LD_*/DYLD_*
- **sha256 drift detection** pour H18 : hashlib.sha256 vs plugin-manifest.json — détecte tampering post-install

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet : `advanced_security.py` + `config_migration.py` + 55 models + 10 modules + 98 tests
- Table outils : 2 nouvelles lignes (Advanced Security 8 tools, Config Migration 5 tools)
- Ce journal de session ajouté

---

### Session du 4 mars 2026 — Phases 5a→5d complètes (feat/phase-5a)

**Accompli :**
Implémentation des 4 phases du plan ANALYSIS-REPORT-v4.md. Total final :
**67 tools / 17 modules / 160 tests à 100 %**. Détail par phase :

- **Phase 5a** : Auth middleware (I2), CI workflow (I19+I20), DRY no_traversal (I1), export mocks (I8)
- **Phase 5b** : Observability pipeline T1/T6, pgvector T3, knowledge graph T9, concurrency tests I9
- **Phase 5c** : Agent orchestration T4, i18n audit T5, skill loader T7
- **Phase 5d** : n8n workflow bridge T8 (export+import), browser context check T10
- **Transversaux** : README sync I4 (55→67 tools), cross-field model validators I5

3 modèles avec `@model_validator(mode="after")` :
`AgentTeamOrchestrateInput` (duplicate IDs + dep refs), `WorkspaceLockInput` (timeout reset),
`SessionConfigCheckInput` (at-least-one-path).

PR #3 (draft) mise à jour sur `feat/phase-5a` — 4 commits séquentiels.

**Décisions d'architecture :**
- **n8n node mapping** : 20 OpenClaw→n8n type mappings (http_request, agent, vector_store, etc.)
  — extensible via `_OPENCLAW_TO_N8N_NODE_MAP` dict
- **Workflow validation bidirectionnelle** : export valide la pipeline avant conversion,
  import valide le JSON n8n avant copie (strict mode par défaut)
- **Browser audit _deep_get** : recherche récursive dans les configs imbriquées (max depth 10)
  — gère Playwright et Puppeteer qui imbriquent les settings différemment
- **13 dangerous browser args** : liste exhaustive des args Chrome/Chromium dangereux
  avec sévérité différenciée (CRITICAL pour --no-sandbox, HIGH pour le reste)
- **Cross-field validators** : silently reset timeout_s pour release/status (pas d'erreur),
  mais reject dur pour deps invalides et paths manquants

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet mise à jour : 17 modules, 67 tools, 160 tests
- Table outils : 7 nouvelles lignes (Observability, Memory, Orchestration, i18n, Skill, n8n, Browser)
- Ce journal de session ajouté

---

### Session du 5 mars 2026 — Phase 7 Disruption: 21 nouveaux tools (feat/phase-7-disruption)

**Accompli :**
Implémentation complète de la Phase 7 du roadmap de disruption (ANALYSIS-REPORT-v6.md).
3 nouveaux modules Python : `a2a_bridge.py` (6 tools A2A Protocol v1.0 RC), `platform_audit.py`
(8 tools alignement platform 2026.2), `ecosystem_audit.py` (7 tools différenciation écosystème).
Total porté à **96 tools / 21 modules / 264 tests à 100 % / v2.0.0**. Protocol MCP upgradé
à `2025-11-25`. SKILL.md `firm-a2a-bridge` créée. Branches pushées sur les deux repos.

**Décisions d'architecture :**
- **A2A Card generation from SOUL.md** : parsing frontmatter YAML + extraction des skills
  via regex `## Skills` — produit un agent card JSON conforme A2A v1.0 RC
- **SSRF protection** : localhost/127.0.0.1/0.0.0.0/::1 bloqués dans `task_send` et `push_config`
- **In-memory stores** : `_TASKS` et `_PUSH_CONFIGS` — suffisant pour un MCP server single-process
- **Platform tools return pattern** : `{ok, severity, findings, finding_count, config_path}`
  — cohérent avec les patterns existants (runtime_audit, gateway_hardening)
- **Ecosystem tools `session_data` dict** : les tools context/cost/budget acceptent un dict
  `session_data` au lieu de params plats — plus flexible pour l'évolution de l'API
- **Provenance tracker** : chaîne de hashes SHA-256 append-only + vérification d'intégrité
- **n8n→MCP firewall** : vérification que les policies MCP couvrent les tool calls

**Améliorations appliquées à ce CLAUDE.md :**
- Structure projet : 3 nouveaux modules + 96 models + 21 modules + 264 tests
- Table outils : 3 nouvelles lignes (A2A Bridge 6 tools, Platform Audit 8 tools, Ecosystem Audit 7 tools)
- Skills : `firm-a2a-bridge` ajouté
- Ce journal de session ajouté

---

## 🔑 PHILOSOPHIE

> "Utilise l'IA aussi agressivement que possible — c'est la seule façon de repousser
> les limites de ce dont les agents sont capables." — Anthropic

Le rôle de l'humain évolue vers : **supervision**, **review de l'output**, **définition
d'architecture**. Délègue les tâches répétitives et bas niveau ; concentre-toi sur ce
qui compte vraiment.

Plus ce fichier `CLAUDE.md` est détaillé et à jour, meilleures sont les performances.
C'est le **levier d'optimisation n°1**.
