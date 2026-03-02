# ANALYSIS-REPORT-v8 — Cross-Repo Audit (Mise à jour 8 mars 2026)

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Résumé flash

| Repo | Tools | Tests | Coverage | CI | Packaging |
|------|-------|-------|----------|-----|-----------|
| **mcp-openclaw-extensions** | 115 | 592 (281 unit + 311 integration) | **100%** | ✅ pyproject.toml + Dockerfile | ✅ pyproject.toml |
| **Memory-os-ai** | 18 | 348 (all pass) | **96%** | ✅ GitHub Actions CI | ✅ pyproject.toml propre |
| **setup-vs-agent-firm** | N/A (factory) | N/A | N/A | ✅ AI review PR | Bash factory + docker-compose |

---

## CRITICAL — Bloquants

### C1. ~~mcp-openclaw-extensions : 254 tests en erreur~~ ✅ RÉSOLU
- **Fix** : websockets lazy import dans `vs_bridge.py` + `gateway_fleet.py` (try/except au top-level)
- **Fix** : fixture `test_smoke.py` détecte le venv Python automatiquement
- **Fix** : smoke tests marqués `@pytest.mark.integration` — séparés des unit tests
- **Résultat** : 281 unit tests pass, 311 integration tests pass (séparément)

### C2. ~~READMEs massivement périmés~~ ✅ RÉSOLU
- **Fix** : les 2 READMEs mis à jour (115 tools, 25 modules, 30 skills)
- **Fix** : CLAUDE.md cohérent avec le code

### C3. ~~Coverage réelle à 27%~~ ✅ RÉSOLU → 100%
- **Fix Sprint 1** : `test_handlers.py` — 108 handler-level tests (27% → 48%)
- **Fix Sprint 2** : `test_cov_main.py` — tests main.py dispatcher (0% → 100%)
- **Fix Sprint 3** : `test_cov_acp.py` + `test_cov_fleet_vs.py` — ACP, fleet, VS bridge (0-17% → 100%)
- **Fix Sprint 4** : `test_cov_hebbian.py` — 4 sous-modules hebbian memory (17-37% → 100%)
- **Fix Sprint 5** : `test_cov_deep.py` — 20+ modules restants (25-92% → 100%)
- **Résultat** : 100% coverage (branch + line), `fail_under = 100` dans pyproject.toml

---

## HIGH — Must-fix

### H1. ~~Zero CI pour Memory-os-ai~~ ✅ RÉSOLU
- **Fix** : `.github/workflows/ci.yml` créé (Python 3.11, pip install, pytest, coverage check)
- Déclenché sur push `main` + PR

### H2. ~~mcp-openclaw-extensions n'est pas un package Python~~ ✅ RÉSOLU
- **Fix** : `pyproject.toml` créé avec metadata, dependencies, console script, pytest config
- **Fix** : `Dockerfile` + `docker-compose.yml` pour déploiement containerisé

### H3. ~~Zero intégration code entre les 3 repos~~ ✅ PARTIELLEMENT RÉSOLU
- **Fix** : `mcp-config-unified.json` — template MCP config enregistrant les 2 serveurs côte-à-côte
- **Fix** : `docker-compose.yml` — lance les 2 serveurs MCP + volumes partagés
- **Reste** : pas de dependency croisée dans le code (by design — repos indépendants)

### H4. ~~ClawHub : 14/30 skills en "pending (rate limit)"~~ ✅ RÉSOLU
- **Fix** : 30/30 skills publiées sur ClawHub (batch publish en 3 rounds)

---

## MEDIUM — Améliorations significatives

### M1. ~~Bridges ChatGPT obsolète~~ ✅ RÉSOLU
- **Fix** : `mcp-connection.json` mis à jour de 14 → 18 tools

### M2. ~~Factory sector list incohérente~~ ✅ RÉSOLU
- **Fix** : README aligné avec la vraie liste de 15 secteurs du code

### M3. Gap count contradictoire dans le parent README
- **Statut** : cosmétique, non bloquant — à corriger dans une prochaine itération

### M4. Pas de dependency pinning robuste
- **Statut** : floor pins acceptables pour un projet non-production — lockfile optionnel

### M5. ~~test_smoke.py : tests d'intégration traités comme unit tests~~ ✅ RÉSOLU
- **Fix** : `pytestmark = pytest.mark.integration` appliqué sur tout test_smoke.py
- **Fix** : `pyproject.toml` configure `-m "not integration"` par défaut

---

## Tendances écosystème 2025-2026 — État mis à jour

| Tendance | État actuel | Statut |
|----------|-------------|--------|
| **MCP Registry / Discovery** | 30 skills sur ClawHub | ✅ Complet |
| **Composable agents (A2A v0.4+)** | 8 tools A2A bridge RC v1.0 | ✅ Complet |
| **Streaming responses** | SSE endpoint + 3 transports | ✅ Complet |
| **Multi-tenant / auth** | OAuth/OIDC audit + Bearer token | ✅ Complet |
| **Observability / tracing** | JSONL→SQLite + CI pipeline check | ✅ Complet |
| **Package distribution** | pyproject.toml + Dockerfile | ✅ Complet |
| **E2E demo / quickstart** | docker-compose.yml + unified config | ✅ Complet |
| **Contribution ecosystem** | CONTRIBUTING.md dans Memory-os-ai | ⚠️ 2/3 repos |

---

## Statistiques détaillées

### mcp-openclaw-extensions — Coverage par module (après sprint coverage)

| Module | Stmts | Coverage |
|--------|-------|----------|
| main.py | 257 | **100%** |
| vs_bridge.py | 110 | **100%** |
| gateway_fleet.py | 184 | **100%** |
| acp_bridge.py | 169 | **100%** |
| compliance_medium.py | 411 | **100%** |
| ecosystem_audit.py | 285 | **100%** |
| memory_audit.py | 201 | **100%** |
| spec_compliance.py | 224 | **100%** |
| platform_audit.py | 276 | **100%** |
| advanced_security.py | 271 | **100%** |
| hebbian_memory/ | 471 | **100%** |
| models.py | 705 | **100%** |
| *tous les 25 modules* | 5848 | **100%** |

### Memory-os-ai — Coverage stable à 96%

| Module | Coverage | Lignes manquantes |
|--------|----------|-------------------|
| chat_extractor.py | 95% | L206-207, 237, 331, 458, 462, 471-472 |
| engine.py | 96% | L121-122, 266-267, 310, 608, 755-756, 764-770 |
| server.py | 94% | L94-96, 760-761, 790-795, 801-803, 806, 834-836, 839, 875 |
| setup.py | 98% | L37, 333 |
