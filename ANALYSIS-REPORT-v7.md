# ANALYSIS-REPORT-v7 — Inefficiencies & Gap Analysis

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

**Date :** 2026-03-07
**Scope :** `mcp-openclaw-extensions` (v2.2.0, 113 tools, 25 modules, 311 tests) + `setup-vs-agent-firm` (11 skills, 5 souls)
**Baseline specs :** MCP 2025-11-25 · A2A RC v1.0 · OpenClaw 2026.2

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Gaps Protocole MCP (vs 2025-11-25)](#2-gaps-protocole-mcp)
3. [Gaps Protocole A2A (v0.4.0 → RC v1.0)](#3-gaps-protocole-a2a)
4. [Inefficiences internes du code](#4-inefficiences-internes)
5. [Gaps Tests & Qualité](#5-gaps-tests--qualité)
6. [Gaps Écosystème & Skills](#6-gaps-écosystème--skills)
7. [Matrice de priorité](#7-matrice-de-priorité)
8. [Plan d'action recommandé](#8-plan-daction-recommandé)

---

## 1. Résumé exécutif

| Métrique | Valeur |
|----------|--------|
| Tools MCP | 113 |
| Modules Python | 25 (18 949 lignes) |
| Tests | 311 (smoke only) |
| Skills publiées | 11/11 (ClawHub v1.0.0) |
| Gaps CRITICAL | **7** |
| Gaps HIGH | **12** |
| Gaps MEDIUM | **9** |
| **Total gaps** | **28** |

Le serveur MCP déclare la spec `2025-11-25` mais n'implémente que la primitive `tools`.
Le bridge A2A est resté sur v0.4.0 alors que la spec a reçu des **breaking changes majeurs**
en v1.0 RC (data model, bindings, extensions). En interne, 6 modules dupliquent
`_load_config`, les tests n'ont aucune couverture fonctionnelle par module, et la convention
de nommage des handlers est incohérente.

---

## 2. Gaps Protocole MCP (vs 2025-11-25)

### CRITICAL

| ID | Gap | Impact | Module |
|----|-----|--------|--------|
| M-C1 | **0/113 tools ont des icons** | UX marketplace dégradée — MCP 2025-11-25 ajoute `icons` sur tools, resources, prompts (SEP-973) | main.py, all modules |
| M-C2 | **Pas de `structuredContent`** dans les réponses tools | Les clients MCP modernes attendent `structuredContent` à côté de `content` (MCP 2025-06-18) | main.py |
| M-C3 | **Aucune capability `resources`** | Le serveur ne peut pas exposer de fichiers/URIs consultables — 0% de la Resource API implémentée | main.py |

### HIGH

| ID | Gap | Impact | Module |
|----|-----|--------|--------|
| M-H1 | **Pas de capability `prompts`** | Impossible d'exposer des templates/prompts réutilisables via MCP | main.py |
| M-H2 | **Pas de `elicitation`** | Le serveur ne peut pas demander des inputs utilisateur pendant l'exécution d'un tool (MCP 2025-06-18, URL mode en 2025-11-25) | main.py |
| M-H3 | **Pas de `tasks` / durable requests** | Pas de support des opérations longues avec statut async (experimental MCP 2025-11-25) | main.py |
| M-H4 | **`listChanged: False`** — pas de notifications | Le serveur ne notifie pas les clients quand la liste d'outils change | main.py |
| M-H5 | **Pas de Resource Links** dans les résultats tools | tools/call ne retourne jamais de `resource_link` embedded — les clients ne peuvent pas naviguer vers des ressources associées | all modules |
| M-H6 | **Pas de SSE polling / resumption** | Pas de support du transport SSE amélioré avec reprise de connexion (MCP 2025-11-25) | main.py |

### MEDIUM

| ID | Gap | Impact | Module |
|----|-----|--------|--------|
| M-M1 | **Pas de header `MCP-Protocol-Version`** | Le serveur n'enforce pas le header de version sur les requêtes HTTP (MCP 2025-06-18) | main.py |
| M-M2 | **Pas de OAuth Client ID Metadata Documents** | Pas de `.well-known/oauth-client-metadata` (MCP 2025-11-25) | — |
| M-M3 | **Pas de sampling/tool-calling** | Capability `sampling` absente — pas de tool calling dans les créations de messages | main.py |
| M-M4 | **`serverInfo.description` trop court** | "VS Code↔OpenClaw bridge · Fleet manager · Delivery export pipeline" — ne mentionne pas les 113 tools, 7 catégories d'audit | main.py |

---

## 3. Gaps Protocole A2A (v0.4.0 → RC v1.0)

### CRITICAL

| ID | Gap | Impact | Module |
|----|-----|--------|--------|
| A-C1 | **Data model breaking change** — `kind` discriminator supprimé | Le bridge génère `"kind": "text"` dans les parts → invalide en RC v1.0 (remplacé par typed objects: `TextPart`, `FilePart`, `DataPart`) | a2a_bridge.py |
| A-C2 | **1 seul protocol binding** (JSON-RPC) | RC v1.0 définit 3 bindings : JSON-RPC, gRPC, HTTP+JSON/REST — le bridge n'en supporte qu'un | a2a_bridge.py |
| A-C3 | **Pas de `SubscribeToTask`** | Le streaming SSE pour suivre un task en temps réel n'est pas implémenté | a2a_bridge.py |
| A-C4 | **Pas de système d'extensions** | RC v1.0 ajoute un framework d'extensions — le bridge ignore complètement cette capacité | a2a_bridge.py |

### HIGH

| ID | Gap | Impact | Module |
|----|-----|--------|--------|
| A-H1 | **Pas de `ListTasks`** opérationnel | Le bridge a un pseudo-list dans `task_status` mais pas l'opération `ListTasks` conforme RC v1.0 avec filtrage | a2a_bridge.py |
| A-H2 | **Push notification CRUD incomplet** | RC v1.0 exige Create/Get/List/Delete push configs — le bridge n'a que Create | a2a_bridge.py |
| A-H3 | **Agent Card v2 non supporté** | Pas de `provider`, `defaultInputModes`, `defaultOutputModes`, `extensions` dans la card | a2a_bridge.py |
| A-H4 | **Pas de signing Agent Card** (JCS + JWS) | RC v1.0 ajoute la signature cryptographique des Agent Cards | a2a_bridge.py |
| A-H5 | **Pas de header `A2A-Version`** | Le bridge ne valide pas/n'envoie pas le header de version du protocole | a2a_bridge.py |
| A-H6 | **`contextId` non implémenté** | RC v1.0 introduit le groupement de tasks par `contextId` — non supporté | a2a_bridge.py |

---

## 4. Inefficiences internes

### CRITICAL

| ID | Inefficience | Impact | Fichiers |
|----|-------------|--------|----------|
| I-C1 | **`_load_config` dupliqué dans 6 modules** | `config_helpers.py` existe (46 lignes, `load_config()`) mais 6 modules définissent encore leur propre `_load_config` locale | advanced_security, auth_compliance, compliance_medium, config_migration, runtime_audit, spec_compliance |

**Détail :** 3 modules importent `config_helpers` ET redéfinissent quand même `_load_config` localement (`advanced_security`, `config_migration`, `runtime_audit`). 3 modules n'importent aucune version partagée (`auth_compliance`, `compliance_medium`, `spec_compliance`). `gateway_hardening` et `security_audit` ont leur propre pattern inline (sans fonction dédiée).

### HIGH

| ID | Inefficience | Impact | Fichiers |
|----|-------------|--------|----------|
| I-H1 | **Convention de nommage handlers incohérente** | 17 handlers utilisent `handle_*` (auth_compliance, compliance_medium, prompt_security, spec_compliance) — 96 utilisent des noms nus | Tous modules |
| I-H2 | **Modules monolithiques > 1000 lignes** | 6 modules dépassent 1000 LoC : hebbian_memory (1560), models (1344), advanced_security (1150), platform_audit (1134), ecosystem_audit (1063), a2a_bridge (1001) | 6 modules |
| I-H3 | **SSRF checks éparpillés** | La vérification SSRF (localhost/127.0.0.1/::1) est codée en dur dans `a2a_bridge.py` mais absente des autres modules qui acceptent des URLs | a2a_bridge.py |
| I-H4 | **Path traversal checks non centralisés** | Vérifications `..` dispersées dans acp_bridge, advanced_security, et les modèles Pydantic — pas de `@validator` unique réutilisable | Multiples |

### MEDIUM

| ID | Inefficience | Impact | Fichiers |
|----|-------------|--------|----------|
| I-M1 | **`gateway_hardening` + `security_audit` chargent les configs inline** | Pas de `_load_config` ni import de `config_helpers` — pattern `Path(...).read_text()` dupliqué | 2 modules |
| I-M2 | **`__init__.py` vide** (1 ligne) | Pas d'exports publics, pas de version, pas de `__all__` | src/__init__.py |
| I-M3 | **Pas de type stubs / py.typed** | Le package n'expose pas de type hints pour les consommateurs externes | — |

---

## 5. Gaps Tests & Qualité

### CRITICAL

| ID | Gap | Impact |
|----|-----|--------|
| T-C1 | **0 tests unitaires par module** | Les 311 tests sont des smoke tests (initialize, tools/list, tools/call edge cases). Aucun test ne vérifie la logique métier des 113 tools. Coverage fonctionnelle estimée : **< 5%** |

### HIGH

| ID | Gap | Impact |
|----|-----|--------|
| T-H1 | **1 seul fichier de test** (`test_smoke.py`) | Aucun `test_a2a_bridge.py`, `test_security_audit.py`, etc. Impossible de cibler un module en CI |
| T-H2 | **Pas de tests d'intégration** | Aucun test end-to-end vérifiant l'interaction entre modules (ex: fleet → delivery → export) |
| T-H3 | **Pas de coverage report** | Pas de `pytest-cov` configuré. Le CLAUDE.md exige 80% mais il n'y a aucun mécanisme pour le vérifier |
| T-H4 | **Pas de fixtures / mocks structurés** | Les tests ne mockent pas les I/O fichier, les appels réseau, ou les configs — impossible de tester sans système de fichiers réel |

### MEDIUM

| ID | Gap | Impact |
|----|-----|--------|
| T-M1 | **Pas de tests de régression** | Si on refactor `_load_config` → DRY, rien ne garantit que le comportement ne change pas |
| T-M2 | **Pas de property-based testing** | Les modèles Pydantic avec regex/contraintes seraient parfaits pour Hypothesis |

---

## 6. Gaps Écosystème & Skills

### MEDIUM

| ID | Gap | Impact |
|----|-----|--------|
| E-M1 | **Skills publiées à v1.0.0** — pas de sync avec les évolutions spec | Les skills ClawHub (firm-a2a-bridge etc.) référencent v0.4.0 mais la spec est RC v1.0 |
| E-M2 | **Pas de SKILL.md pour les nouveaux modules** | Modules `spec_compliance`, `prompt_security`, `auth_compliance`, `compliance_medium` n'ont pas de skill publiable |
| E-M3 | **Pas de CHANGELOG.md** dans le repo extensions | Historique uniquement dans les commits git — pas de changelog structuré pour les consommateurs |

---

## 7. Matrice de priorité

```
                    IMPACT
                Low    Medium    High    Critical
           ┌─────────┬─────────┬─────────┬─────────┐
 Quick     │         │ I-M2    │ I-C1    │ M-C1    │
 (< 2h)    │         │ I-M3    │ I-H1    │         │
           ├─────────┼─────────┼─────────┼─────────┤
 Medium    │         │ T-M1    │ M-H4    │ M-C2    │
 (2-8h)    │         │ T-M2    │ M-H5    │ M-C3    │
           │         │ E-M3    │ I-H3    │ T-C1    │
           │         │ M-M4    │ I-H4    │         │
           │         │ E-M2    │ A-H5    │         │
           ├─────────┼─────────┼─────────┼─────────┤
 Long      │         │ M-M1    │ M-H1    │ A-C1    │
 (> 8h)    │         │ M-M2    │ M-H2    │ A-C2    │
           │         │ M-M3    │ M-H3    │ A-C3    │
           │         │         │ M-H6    │ A-C4    │
           │         │         │ A-H1-6  │         │
           │         │         │ I-H2    │         │
           │         │         │ T-H1-4  │         │
           │         │         │ E-M1    │         │
           └─────────┴─────────┴─────────┴─────────┘
```

---

## 8. Plan d'action recommandé

### Sprint 1 — Quick Wins (1-2 jours)

| # | Action | Cible | Effort |
|---|--------|-------|--------|
| 1 | **Ajouter `icons`** sur les 113 tools (emoji ou data URI SVG) | M-C1 | 2h |
| 2 | **Refactor DRY `_load_config`** — supprimer les 6 copies locales, utiliser `config_helpers.load_config` partout | I-C1, I-M1 | 2h |
| 3 | **Uniformiser nommage handlers** — tout en bare function names (supprimer les 17 `handle_` prefixes) | I-H1 | 1h |
| 4 | **Ajouter `__all__`** + `py.typed` marker | I-M2, I-M3 | 30min |
| 5 | **Mise à jour `serverInfo.description`** | M-M4 | 15min |
| 6 | **Créer `CHANGELOG.md`** | E-M3 | 30min |

### Sprint 2 — MCP Protocol Compliance (3-5 jours)

| # | Action | Cible | Effort |
|---|--------|-------|--------|
| 7 | **Implémenter `structuredContent`** dans le dispatcher `tools/call` | M-C2 | 4h |
| 8 | **Ajouter capability `resources`** — exposer au minimum les configs et les SKILL.md comme resources | M-C3 | 8h |
| 9 | **Ajouter capability `prompts`** — templates d'audit configurables | M-H1 | 4h |
| 10 | **Resource links** dans les réponses tools | M-H5 | 4h |
| 11 | **`listChanged: True`** + notifications SSE | M-H4 | 4h |
| 12 | **Centraliser SSRF guard** dans `config_helpers.py` | I-H3 | 2h |
| 13 | **Centraliser path traversal** validator Pydantic | I-H4 | 2h |

### Sprint 3 — A2A RC v1.0 Rewrite (5-8 jours)

| # | Action | Cible | Effort |
|---|--------|-------|--------|
| 14 | **Réécrire le data model** — supprimer `kind` discriminator, adopter `TextPart`/`FilePart`/`DataPart` | A-C1 | 8h |
| 15 | **Ajouter HTTP+JSON/REST binding** | A-C2 (partiel) | 8h |
| 16 | **Implémenter `SubscribeToTask`** (SSE streaming) | A-C3 | 8h |
| 17 | **Système d'extensions** | A-C4 | 4h |
| 18 | **Agent Card v2** (provider, defaultInputModes, extensions, signing) | A-H3, A-H4 | 6h |
| 19 | **`ListTasks` + Push CRUD complet** | A-H1, A-H2 | 4h |
| 20 | **`contextId` + header `A2A-Version`** | A-H5, A-H6 | 2h |
| 21 | **Mettre à jour SKILL.md `firm-a2a-bridge`** → v2.0.0 | E-M1 | 1h |

### Sprint 4 — Tests & Qualité (3-5 jours)

| # | Action | Cible | Effort |
|---|--------|-------|--------|
| 22 | **Créer 1 fichier test par module** (25 fichiers) avec au min 3 tests positifs + 1 négatif | T-C1, T-H1 | 16h |
| 23 | **Configurer `pytest-cov`** avec seuil 80% et badge README | T-H3 | 1h |
| 24 | **Ajouter fixtures / conftest.py** avec mocks filesystem + HTTP | T-H4 | 4h |
| 25 | **Tests d'intégration** fleet→delivery et security→audit pipelines | T-H2 | 8h |
| 26 | **Hypothesis tests** sur les 113 modèles Pydantic | T-M2 | 4h |

### Sprint 5 — Advanced MCP Features (4-6 jours)

| # | Action | Cible | Effort |
|---|--------|-------|--------|
| 27 | **Elicitation** — demander des inputs utilisateur pendant l'exécution | M-H2 | 8h |
| 28 | **Tasks / durable requests** — support des opérations longues | M-H3 | 8h |
| 29 | **SSE polling / resumption** | M-H6 | 6h |
| 30 | **MCP-Protocol-Version header** enforcement | M-M1 | 2h |
| 31 | **Refactoring modules > 1000 LoC** — split en sous-modules | I-H2 | 8h |
| 32 | **Publier nouvelles skills** (spec-compliance-pack, prompt-security-pack) | E-M2 | 2h |

---

## Résumé des compteurs par sprint

| Sprint | Gaps fermés | Effort estimé |
|--------|-------------|---------------|
| Sprint 1 — Quick Wins | 7 | 1-2 jours |
| Sprint 2 — MCP Compliance | 7 | 3-5 jours |
| Sprint 3 — A2A RC v1.0 | 8 | 5-8 jours |
| Sprint 4 — Tests | 6 | 3-5 jours |
| Sprint 5 — Advanced MCP | 6 | 4-6 jours |
| **TOTAL** | **28 + 6 supplémentaires** | **16-26 jours** |

---

*Fin du rapport. Branche recommandée : `feat/analysis-v7`*
