# CAHIER DES CHARGES
## Système de Mémoire Adaptative Hebbienne + Base Vectorielle pour Claude.md

Version : 1.0.0 — Draft initial  
Date : 28 février 2026  
Destinataire : Agent Orchestrateur  
Statut : Prêt pour implémentation

---

# 1. Contexte et Problématique

## 1.1 Situation actuelle

Claude Code utilise un fichier Claude.md comme mémoire contextuelle inter-sessions. Ce fichier est aujourd'hui statique : il est écrit une fois manuellement, ne s'adapte pas à l'usage réel, et ne capitalise pas sur les patterns qui émergent au fil du travail.

Ce projet vise à rendre ce fichier vivant, auto-évolutif et fondé sur des mécanismes inspirés des neurosciences.

## 1.2 Insuffisances identifiées

- Absence de mémoire épisodique inter-sessions : chaque démarrage repart de zéro
- Règles obsolètes non purgées : le Claude.md grossit sans jamais s'élaguer
- Patterns implicites non capturés : les bonnes pratiques émergentes restent dans la tête des devs
- Aucune pondération : toutes les instructions ont le même poids, quelle que soit leur utilité réelle

## 1.3 Inspiration neurobiologique

Le système s'inspire de deux mécanismes cérébraux complémentaires.

La plasticité hebbienne correspond au renforcement synaptique par co-activation, ce qui se traduit dans notre système par les poids des règles dans Claude.md. La mémoire hippocampique assure le stockage épisodique des événements, représentée ici par la base de données vectorielle pgvector. La consolidation néocorticale transforme les épisodes en schémas durables, ce qui correspond au job d'analyse hebbienne périodique.

---

# 2. Objectifs du Système

## 2.1 Objectifs fonctionnels

- OF-01 : Persister la mémoire des sessions de travail dans une BDD vectorielle
- OF-02 : Analyser automatiquement les patterns co-occurrents entre sessions
- OF-03 : Mettre à jour les poids des règles Claude.md selon l'usage réel
- OF-04 : Supprimer automatiquement les règles obsolètes (atrophie hebbienne)
- OF-05 : Promouvoir les patterns émergents en règles explicites
- OF-06 : Conserver un verrou humain sur les modifications structurelles critiques

## 2.2 Objectifs non-fonctionnels

- ONF-01 : Traçabilité complète via Git de toute modification du Claude.md
- ONF-02 : Latence d'injection mémoire inférieure à 200ms pour ne pas ralentir Claude Code
- ONF-03 : Sécurité — aucune donnée sensible dans les embeddings (PII strippé)
- ONF-04 : Réversibilité totale — tout changement automatique est annulable
- ONF-05 : Fonctionnement offline-first — BDD locale en priorité

---

# 3. Architecture Technique

## 3.1 Vue d'ensemble des composants

Pipeline global (séquentiel) :

```
[ Session Claude Code ]
         ↓ fin de session
[ Session Harvester ] → extrait résumé + tags + règles activées
         ↓
[ Vector Store (pgvector) ] → stockage épisodique embeddings
         ↓ job hebdomadaire
[ Hebbian Analyzer ] → clustering + calcul poids
         ↓
[ Claude.md Writer ] → mise à jour couches 2 & 3
         ↓ si promotion/suppression
[ Human Review Gate ] → validation humaine obligatoire
```

## 3.2 Stack technologique

BDD vectorielle : pgvector (PostgreSQL) — SQL natif, pas de dépendance externe, robuste  
Embeddings : text-embedding-3-small (OpenAI) ou BGE-M3 local — rapport qualité/coût optimal  
Clustering : HDBSCAN — pas besoin de fixer k, gère le bruit  
Orchestration jobs : n8n ou script Python cron — transparent, auditable  
Analyse patterns : Claude API (claude-sonnet-4-6) — compréhension sémantique du code  
Versioning Claude.md : Git (commit automatique) — auditabilité totale des changements

## 3.3 Structure du Claude.md augmenté — 4 couches

### Couche 1 — CORE (immuable, humain uniquement)

```
# ═══════════════════════════════════════════
# LAYER 1 — CORE (immuable)
# Modifiable uniquement par validation humaine
# ═══════════════════════════════════════════

## Stack
- Framework: [à remplir]
- Conventions: [à remplir]

## Règles non-négociables
- Jamais de secrets en clair dans le code
- Toujours partir d'un git state propre
- Un commit par unité logique de travail
```

### Couche 2 — CONSOLIDATED PATTERNS (hebbian, auto-mise à jour)

```
# ═══════════════════════════════════════════
# LAYER 2 — CONSOLIDATED PATTERNS
# Mis à jour automatiquement | Sessions: {N}
# Dernière analyse: {DATE}
# ═══════════════════════════════════════════

## Patterns forts [poids > 0.8]
- [0.94] Debugging prod → toujours demander stack trace avant fix
- [0.89] Nouvelle feature → TDD, écrire les tests avant le code

## Patterns émergents [poids 0.4–0.8]
- [0.61] Revue de PR → vérifier couverture de tests

## En atrophie [poids < 0.2] → suppression planifiée
- [0.08] Prettier pre-commit hook (désactivé depuis 3 mois)
```

### Couche 3 — EPISODIC INDEX (pointeurs BDD, jamais le contenu brut)

```
# ═══════════════════════════════════════════
# LAYER 3 — EPISODIC INDEX
# NE PAS MODIFIER MANUELLEMENT
# ═══════════════════════════════════════════

## Sessions haute valeur récentes [similarity > 0.85]
- sid:a3f9c2 | 'Migration PostgreSQL résolue en 2h'
  tags: [migration, prod, urgent] | validé: ✅
- sid:b7e1d4 | 'Auth JWT avec refresh tokens'
  tags: [sécurité, auth] | validé: ✅

## En attente de consolidation
- sid:f2a8b1 | 'Rate limiting — abandonné'
  tags: [API, perf] | validé: ❌
```

### Couche 4 — META INSTRUCTIONS (self-update rules)

```
# ═══════════════════════════════════════════
# LAYER 4 — META INSTRUCTIONS
# Instructions pour l'agent de fin de session
# ═══════════════════════════════════════════

## En fin de session, l'agent doit:
1. Résumer en max 3 lignes + tags
2. Identifier les règles LAYER 2 activées
3. Incrémenter leur poids de +0.05
4. Décrémenter les non-activées de -0.02
5. Si poids > 0.95 → proposer promotion CORE (humain)
6. Si poids < 0.10 → marquer pour suppression (humain)
7. Proposer un pattern si action répétée 3x sans règle

## Seuils de consolidation
- Épisodique → Émergent : activé 5 sessions consécutives
- Émergent → Fort : poids > 0.8 sur 20 sessions
- Fort → CORE : validation humaine obligatoire
```

---

# 4. Spécifications Fonctionnelles Détaillées

## 4.1 Module Session Harvester

Déclenché automatiquement à la fin de chaque session Claude Code (hook post-session ou cron toutes les heures si session longue).

Entrées requises :
- Transcript complet de la session (stdin ou fichier log)
- État git avant/après (diff)
- Résultat des tests (exit code + rapport)
- Claude.md actuel (pour identifier les règles activées)

Sorties produites :
- Résumé de session (3 lignes max, JSON)
- Tags extraits (liste de strings)
- Règles Layer 2 activées (liste d'IDs avec poids actuels)
- Embedding de la session (vecteur float[])
- Score de qualité (0–1, basé sur tests passing + commit propre)

## 4.2 Module Vector Store

Schéma de la table PostgreSQL principale :

```sql
CREATE TABLE sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  summary       TEXT NOT NULL,
  tags          TEXT[] NOT NULL DEFAULT '{}',
  embedding     VECTOR(1536) NOT NULL,
  quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 1),
  validated     BOOLEAN DEFAULT NULL,
  rules_activated TEXT[] DEFAULT '{}',
  git_diff_hash TEXT,
  archived      BOOLEAN DEFAULT FALSE
);

-- Index pour recherche par similarité
CREATE INDEX ON sessions USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

## 4.3 Module Hebbian Analyzer (job hebdomadaire)

- Charge toutes les sessions non-archivées des 90 derniers jours
- Calcule les co-activations : quelles règles sont activées ensemble ?
- Lance HDBSCAN sur les embeddings pour identifier les clusters thématiques
- Pour chaque cluster : propose un label de pattern (via Claude API)
- Met à jour les poids selon la formule hebbienne :

```python
# Formule de mise à jour des poids
nouveau_poids = ancien_poids + (learning_rate * activation) - (decay * (1 - activation))

# Paramètres par défaut
learning_rate = 0.05   # Renforcement si activée
decay         = 0.02   # Atrophie si non-activée
poids_min     = 0.0    # Floor — suppression si < 0.10
poids_max     = 0.95   # Ceiling — promotion CORE si > 0.95
```

## 4.4 Module Claude.md Writer

- Lit le Claude.md actuel et parse les 4 couches (regex sur les headers)
- Met à jour uniquement Layer 2 et Layer 3 automatiquement
- Layer 1 et Layer 4 : lecture seule pour le système automatique
- Crée un commit Git signé avec message standardisé :

```
chore(claude-md): hebbian update — session {ID}

# Changed rules:
- rule:debugging-stack-trace: 0.87 → 0.92 (+0.05)
- rule:prettier-hook: 0.12 → 0.10 (-0.02) [atrophie]

# New emergent pattern proposed:
- rule:tdd-before-feature: first seen in 5 consecutive sessions

Co-authored-by: HebbianAnalyzer <agent@system>
```

## 4.5 Human Review Gate

Validation humaine obligatoire pour :
- Toute promotion d'un pattern vers Layer 1 (CORE)
- Toute suppression définitive d'une règle (poids < 0.10 pendant 4 semaines)
- Tout nouveau pattern proposé avec un label ambigu (score confiance < 0.7)
- Toute modification structurelle des Layer 3 ou 4

Le système génère une Pull Request GitHub avec un résumé lisible des changements proposés. Le dev approuve, rejette, ou modifie avant merge.

---

# 5. Garde-fous et Sécurité

## 5.1 Anti-dérive

- Aucune règle ne peut atteindre poids = 1.0 automatiquement (max 0.95)
- Toute série de 3 changements automatiques consécutifs déclenche une review forcée
- Snapshot mensuel complet du Claude.md archivé en Git tag
- Détecteur de drift : alerte si le cosine similarity entre Claude.md v(t) et v(t-30j) est inférieur à 0.7

## 5.2 Sécurité des données

- Stripping PII obligatoire avant embedding (regex + NER model)
- Secrets détectés (API keys, passwords) → session rejetée, alerte immédiate
- BDD vectorielle accessible uniquement en localhost ou VPN
- Rotation des embeddings si fuite suspectée (ré-embedding de toutes les sessions)

## 5.3 Réversibilité

- Chaque modification Claude.md = 1 commit Git atomique
- Commande de rollback : git revert HEAD --no-edit relance le recalcul des poids
- Mode dry-run disponible : simule les changements sans les appliquer

---

# 6. Prompt Complet pour l'Agent Orchestrateur

## 6.1 System Prompt — Agent Orchestrateur

```
# SYSTEM PROMPT — HEBBIAN MEMORY ORCHESTRATOR AGENT
# Version: 1.0.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## IDENTITÉ ET MISSION
Tu es l'agent orchestrateur du système de mémoire adaptative Hebbienne.
Ta mission est de maintenir le fichier Claude.md comme une mémoire vivante
qui s'améliore automatiquement à chaque session de développement,
en t'inspirant des mécanismes de plasticité synaptique hebbienne.

Tu opères en pipeline : Session → Harvest → Store → Analyze → Update → Review.
Tu es le chef d'orchestre de ce pipeline. Tu ne modifies jamais directement
le Layer 1 (CORE) du Claude.md sans validation humaine explicite.

## OUTILS DISPONIBLES
- harvest_session(transcript, git_diff, test_results) → SessionData
- embed_text(text) → vector<float[]>
- store_session(session_data, embedding) → session_id
- search_similar(embedding, limit=10) → Session[]
- run_hebbian_analysis(since_days=90) → PatternAnalysis
- update_claude_md(layer, changes) → GitCommit
- create_review_pr(proposed_changes) → PullRequestURL
- notify_human(message, urgency='normal') → void

## WORKFLOW PRINCIPAL — FIN DE SESSION

Exécute ce workflow à chaque fin de session Claude Code :

### ÉTAPE 1 — HARVEST
Appelle harvest_session() avec les données de la session terminée.
Extrais les informations suivantes :
  - summary: résumé en 2-3 phrases maximum
  - tags: liste de 3-7 tags décrivant le contenu (ex: [debugging, postgres, migration])
  - rules_activated: liste des IDs de règles Layer 2 que cette session a utilisées
  - quality_score: entre 0 et 1
    → 1.0 si tous les tests passent ET commit propre
    → 0.7 si tests passent partiellement
    → 0.3 si session abandonnée ou tests en échec
    → 0.0 si erreur critique non résolue

### ÉTAPE 2 — EMBED ET STORE
Génère l'embedding du résumé+tags concaténés.
Stocke la session dans pgvector avec store_session().
Retourne le session_id pour traçabilité.

### ÉTAPE 3 — MISE À JOUR INCRÉMENTALE DES POIDS
Lis le Layer 2 du Claude.md actuel.
Pour chaque règle :
  - SI activée cette session : nouveau_poids = min(poids + 0.05, 0.95)
  - SI non activée : nouveau_poids = max(poids - 0.02, 0.0)
Applique update_claude_md('layer2', changes) avec les nouveaux poids.
Le commit Git est automatique avec message standardisé.

### ÉTAPE 4 — DÉTECTION DE PATTERNS ÉMERGENTS
Compte les occurrences de chaque action sans règle existante.
SI une action se répète 3 fois dans des sessions récentes :
  Propose un nouveau pattern avec label et poids initial 0.30.
  Crée une PR via create_review_pr() pour validation humaine.
  NE PAS ajouter directement au Claude.md sans approbation.

## WORKFLOW PÉRIODIQUE — ANALYSE HEBBIENNE (hebdomadaire)

Exécute ce workflow chaque lundi à 03:00 :

### ÉTAPE A — CLUSTERING
Appelle run_hebbian_analysis(since_days=90).
Identifie les clusters de sessions par similarité sémantique.
Pour chaque cluster de 5+ sessions : génère un label de pattern.

### ÉTAPE B — CONSOLIDATION
Pour chaque pattern identifié :
  - SI déjà en Layer 2 : renforce le poids proportionnellement
  - SI nouveau et fréquence > 5 sessions : propose via PR
  - SI absent depuis 30 jours : marque en atrophie

### ÉTAPE C — GESTION DE L'ATROPHIE
Pour chaque règle Layer 2 avec poids < 0.10 :
  - SI atrophie confirmée depuis 4 semaines consécutives :
    → Notifie le human via notify_human() avec urgency='low'
    → Propose suppression via PR (jamais suppression directe)

### ÉTAPE D — PROMOTIONS POTENTIELLES
Pour chaque règle Layer 2 avec poids > 0.90 :
  Crée une PR proposant la promotion vers Layer 1 (CORE).
  Message : 'Cette règle est activée dans {X}% des sessions.
  Considérer intégration permanente en CORE ?'
  Attends validation humaine. Ne jamais auto-promouvoir.

## RÈGLES ABSOLUES — NE JAMAIS VIOLER

1. JAMAIS modifier Layer 1 (CORE) sans confirmation humaine explicite
2. JAMAIS supprimer une règle sans PR et validation humaine
3. JAMAIS stocker de secrets, tokens, ou PII dans les embeddings
4. JAMAIS dépasser poids_max = 0.95 par incrémentation automatique
5. TOUJOURS créer un commit Git pour chaque modification du Claude.md
6. TOUJOURS logguer chaque action avec timestamp et session_id
7. En cas de doute sur une action : notifie l'humain, n'agis pas

## FORMAT DE RÉPONSE STANDARD

À chaque exécution du workflow, retourne un rapport JSON :
{
  "pipeline_run_id": "uuid",
  "timestamp": "ISO8601",
  "workflow_type": "end_of_session | weekly_analysis",
  "session_id": "uuid | null",
  "rules_updated": [{"id": "rule-id", "old": 0.87, "new": 0.92}],
  "patterns_proposed": [{"label": "...", "confidence": 0.0}],
  "rules_flagged_atrophy": ["rule-id"],
  "promotions_proposed": ["rule-id"],
  "pr_created": "url | null",
  "git_commit": "hash | null",
  "errors": [],
  "human_action_required": boolean
}

## COMPORTEMENT EN CAS D'ERREUR

- Erreur BDD vectorielle : log, skip l'embedding, continue sans stocker
- Erreur Git commit : STOP, notify_human(urgency='high'), ne pas modifier Claude.md
- Erreur embed API : retry x3, puis log et skip cette session
- Détection de secret dans transcript : STOP immédiat, notify_human(urgency='critical')
- Drift détecté (similarity < 0.7 vs baseline) : notify_human(urgency='high')
```

## 6.2 Prompt d'initialisation (bootstrap)

À exécuter une seule fois pour initialiser le système sur un projet existant :

```
# BOOTSTRAP PROMPT — Initialisation système mémoire adaptative
# À exécuter UNE SEULE FOIS sur un projet existant

Tu vas initialiser le système de mémoire hebbienne sur ce projet.
Voici le Claude.md existant : {CLAUDE_MD_CONTENT}

## TÂCHE 1 — Structuration initiale
Restructure le Claude.md existant en 4 couches :
- Layer 1 (CORE) : toutes les règles actuelles avec poids initial 0.50
- Layer 2 (CONSOLIDATED) : vide au démarrage
- Layer 3 (EPISODIC INDEX) : vide au démarrage
- Layer 4 (META INSTRUCTIONS) : copie les instructions de self-update standard

## TÂCHE 2 — Initialisation BDD
Crée le schéma pgvector si inexistant.
Vérifie la connexion avec : SELECT version();
Confirme l'extension : CREATE EXTENSION IF NOT EXISTS vector;

## TÂCHE 3 — Baseline snapshot
Crée un Git tag : git tag claude-md-baseline-v1.0
Ce tag sert de référence pour la détection de drift futur.

## TÂCHE 4 — Validation
Retourne un rapport de bootstrap avec :
- Nombre de règles migrées en Layer 1
- Confirmation connexion pgvector
- Hash du commit baseline
- Prochaine exécution planifiée du job hebdomadaire
```

---

# 7. Plan d'Implémentation

Phase 1 — Infrastructure BDD : pgvector installé, schéma créé, connexion validée. Durée : 1 jour. Priorité : P0.

Phase 2 — Session Harvester : script de fin de session, extraction summary+tags. Durée : 2 jours. Priorité : P0.

Phase 3 — Embedding pipeline : intégration API embedding, stockage vecteurs. Durée : 1 jour. Priorité : P0.

Phase 4 — Claude.md restructuration : migration 4 couches, bootstrap script. Durée : 1 jour. Priorité : P0.

Phase 5 — Hebbian Analyzer : job hebdo, calcul poids, mise à jour Layer 2. Durée : 3 jours. Priorité : P1.

Phase 6 — Human Review Gate : intégration GitHub PR automatique. Durée : 2 jours. Priorité : P1.

Phase 7 — Monitoring et alertes : dashboard poids, drift detector, logs. Durée : 2 jours. Priorité : P2.

MVP recommandé (P0 uniquement, environ 5 jours) : les phases 1 à 4 constituent un MVP fonctionnel. La mémoire épisodique est active et les poids Layer 2 sont mis à jour après chaque session. Les phases P1 et P2 (analyse hebbienne complète et PR humain) peuvent suivre en itération 2.

---

Cahier des charges v1.0.0 — Système Mémoire Adaptative Hebbienne
