# ANALYSIS-REPORT-v8 — Cross-Repo Audit (2 mars 2026)

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Résumé flash

| Repo | Tools | Tests | Coverage | CI | Packaging |
|------|-------|-------|----------|-----|-----------|
| **mcp-openclaw-extensions** | 115 | 486 (225 pass, **254 errors**) | **27%** | Aucun standalone | ❌ Pas de pyproject.toml |
| **Memory-os-ai** | 18 | 348 (all pass) | **96%** | ❌ Aucun | ✅ pyproject.toml propre |
| **setup-vs-agent-firm** | N/A (factory) | N/A | N/A | ✅ AI review PR | Bash factory |

---

## CRITICAL — Bloquants

### C1. mcp-openclaw-extensions : 254 tests en erreur
- `test_smoke.py` : le fixture lance le serveur avec `sys.executable` → utilise le mauvais venv → **toutes les 254+ smoke tests crashent**
- `test_vs_bridge.py` + `test_gateway_fleet.py` : `import websockets` en dur au top-level → **crash d'import** quand websockets absent
- **Impact** : le repo annonce 484 tests, en réalité seulement **168 passent** (les unit tests)

### C2. READMEs massivement périmés
| Fichier | Annonce | Réalité |
|---------|---------|---------|
| mcp-openclaw-extensions/README.md | 75 tools, 19 modules, 207 tests | **115 tools, 25 modules, 486 tests** |
| setup-vs-agent-firm/README.md | 75 tools, 207 tests, 10 skills | **115 tools, 486 tests, 30 skills** |
| CLAUDE.md | 28 skills | **30 skills** sur disque |

### C3. Coverage réelle à 27% (objectif CLAUDE.md : 80%)
- `pytest.ini` met `fail-under=35` → **même ce seuil n'est pas atteint** (27%)
- 9 modules sous 10% de coverage (compliance_medium 6%, ecosystem_audit 8%, platform_audit 9%…)
- Les tests unitaires ne testent que les modèles Pydantic et les registres TOOLS — **aucun handler logic n'est testé**

---

## HIGH — Must-fix

### H1. Zero CI pour Memory-os-ai
- 348 tests, 96% coverage, mais **aucun GitHub Actions workflow**
- Un push sur `main` peut casser le repo sans que personne ne le sache
- Le repo a le meilleur packaging des 3 (pyproject.toml, Dockerfile, CLI) mais zéro protection

### H2. mcp-openclaw-extensions n'est pas un package Python
- Pas de `pyproject.toml`, pas de `setup.py` — lancé via `python -m src.main`
- Impossible à installer avec `pip install`, impossible à distribuer proprement
- Les dépendances dans `requirements.txt` utilisent des floor pins (`>=`) sans lockfile

### H3. Zero intégration code entre les 3 repos
- **Aucune référence croisée dans le code** entre Memory-os-ai et mcp-openclaw-extensions
- La factory mentionne Memory OS AI en commentaire dans le prompt CEO mais ne l'installe pas
- Pas de config MCP partagée qui enregistre les 2 serveurs côte-à-côte
- Un utilisateur qui installe les 3 repos doit tout câbler manuellement

### H4. ClawHub : 14/30 skills en "pending (rate limit)"
- La session du 7 mars a tenté le batch publish mais le rate limit a frappé
- Presque la moitié des skills n'est pas publiée sur le marketplace

---

## MEDIUM — Améliorations significatives

### M1. Bridges ChatGPT obsolète
- `bridges/chatgpt/mcp-connection.json` dit "14 tools" → réalité 18

### M2. Factory sector list incohérente
- Le README montre `gaming|edtech|healthtech|proptech` dans le `--help`
- Le code valide `generic legal medtech ecommerce fintech saas manufacturing education realestate logistics media automotive energy hr consulting` — liste complètement différente

### M3. Gap count contradictoire dans le parent README
- Titre : "33 gaps" / Sous-titre : "47 documented gaps" / Tables : 46 gap IDs

### M4. Pas de dependency pinning robuste
- mcp-openclaw-extensions : `httpx>=0.27.0` (floor pins, pas de hash)
- Memory-os-ai : floor pins en pyproject.toml, mais `requirements_cpu.txt` a des pins exacts (bon)
- Aucun `uv.lock` ou `pip-tools` requirements.lock

### M5. test_smoke.py : 4800 lignes, tests d'intégration traités comme unit tests
- Pas de `pytest.mark.integration` → impossible de les séparer en CI
- Le fixture utilise `sys.executable` au lieu du venv Python → casse sur tout env autre que le dev local

---

## Tendances écosystème 2025-2026 — Ce qui manque

| Tendance | État actuel | Ce qui manque |
|----------|-------------|---------------|
| **MCP Registry / Discovery** | Skills sur ClawHub | Pas de `mcpx.json` manifest standard pour l'auto-discovery |
| **Composable agents (A2A v0.4+)** | 8 tools A2A bridge | Pas de demo end-to-end d'un agent qui call un autre agent |
| **Streaming responses** | 3 transports (stdio/SSE/HTTP) | Pas de streaming token-by-token dans les tools MCP |
| **Multi-tenant / auth** | OAuth/OIDC audit tools | Pas d'auth réelle sur le serveur Memory-os-ai (MEMORY_API_KEY optionnel) |
| **Observability / tracing** | JSONL→SQLite tool | Pas d'OpenTelemetry intégré dans les 2 serveurs MCP |
| **Package distribution** | pip install pour Memory-os-ai | mcp-openclaw-extensions non installable via pip |
| **E2E demo / quickstart** | Setup CLI + bridges | Pas de `docker-compose.yml` qui lance les 3 repos ensemble |
| **Contribution ecosystem** | CONTRIBUTING.md dans Memory-os-ai | Pas de CONTRIBUTING dans les 2 autres repos |

---

## Statistiques détaillées

### mcp-openclaw-extensions — Coverage par module (unit tests seuls)

| Module | Stmts | Miss | Coverage |
|--------|-------|------|----------|
| main.py | ~400 | ~400 | **0%** |
| vs_bridge.py | 106 | 106 | **0%** |
| gateway_fleet.py | ~150 | ~150 | **0%** |
| compliance_medium.py | 411 | 385 | **6%** |
| ecosystem_audit.py | 285 | 262 | **8%** |
| memory_audit.py | 201 | 184 | **8%** |
| spec_compliance.py | 224 | 206 | **8%** |
| platform_audit.py | 276 | 251 | **9%** |
| advanced_security.py | 269 | 242 | **10%** |

### Memory-os-ai — Lignes non couvertes (4%)

| Module | Coverage | Lignes manquantes |
|--------|----------|-------------------|
| chat_extractor.py | 95% | L206-207, 237, 331, 458, 462, 471-472 |
| engine.py | 96% | L121-122, 266-267, 310, 608, 755-756, 764-770 |
| server.py | 94% | L94-96, 760-761, 790-795, 801-803, 806, 834-836, 839, 875 |
| setup.py | 98% | L37, 333 |
