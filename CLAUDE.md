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
│   └── firm-acp-bridge/             ← protocoles ACP persistence + cron + locking (C4,H3,H4,H5)
├── souls/                           ← 5 SOUL.md (CEO, CFO, CTO, Legal, HR)
├── .github/workflows/
│   └── openclaw-review.yml          ← Quality dept review on every PR
└── mcp-openclaw-extensions/         ← repo séparé (git submodule optionnel)
    ├── src/
    │   ├── security_audit.py        ← 4 tools sécurité (C1,C2,C3,H8)
    │   ├── acp_bridge.py            ← 6 tools ACP + fleet (C4,H3,H4,H5)
    │   ├── reliability_probe.py     ← 4 tools fiabilité + ADR (H6,H7,M1,M5,M6)
    │   ├── models.py                ← 30 modèles Pydantic + TOOL_MODELS
    │   └── main.py                  ← 6 modules, 30 tools enregistrés
    └── tests/
        └── test_smoke.py            ← 39 tests, 100% pass
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
- [ ] PR créée en **draft** avec label `needs-review`

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

## �🔑 PHILOSOPHIE

> "Utilise l'IA aussi agressivement que possible — c'est la seule façon de repousser
> les limites de ce dont les agents sont capables." — Anthropic

Le rôle de l'humain évolue vers : **supervision**, **review de l'output**, **définition
d'architecture**. Délègue les tâches répétitives et bas niveau ; concentre-toi sur ce
qui compte vraiment.

Plus ce fichier `CLAUDE.md` est détaillé et à jour, meilleures sont les performances.
C'est le **levier d'optimisation n°1**.
