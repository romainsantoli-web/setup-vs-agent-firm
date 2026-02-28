#!/usr/bin/env bash
# ============================================================
# firm-factory — génère une firm VS Code Copilot complète
# Usage: ./generate-firm.sh [OPTIONS]
# Voir --help pour la liste complète des options
# ============================================================
set -euo pipefail

# ── couleurs ────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
SECTORS_DIR="$SCRIPT_DIR/sectors"

# ── defaults ────────────────────────────────────────────────
SECTOR="generic"
STACK="typescript"
SIZE="startup"          # startup | scaleup | enterprise
OUTPUT_DIR="."
LANG="fr"               # fr | en
DRY_RUN=false
FORCE=false

# ── help ────────────────────────────────────────────────────
usage() {
cat <<EOF
${CYAN}firm-factory${NC} — Génère une firm VS Code Copilot pyramidale complète

Usage:
  ./generate-firm.sh [OPTIONS]

Options:
  --sector <name>     Secteur cible (défaut: generic)
                      Valeurs: generic, legal, medtech, ecommerce, fintech, saas,
                               manufacturing, education, realestate, logistics,
                               media, automotive, energy, hr, consulting
  --stack  <name>     Stack technique (défaut: typescript)
                      Valeurs: typescript, python, java, dotnet, go, rust, mixed
  --size   <level>    Taille de la firm (défaut: startup)
                      Valeurs: startup (4 depts), scaleup (8 depts), enterprise (all 14)
  --output <dir>      Répertoire de sortie (défaut: .)
  --lang   <code>     Langue des agents (défaut: fr) — fr | en
  --dry-run           Affiche ce qui serait généré sans écrire
  --force             Écrase les fichiers existants
  -h, --help          Affiche cette aide

Exemples:
  ./generate-firm.sh --sector legal --size scaleup --output /my/project
  ./generate-firm.sh --sector fintech --stack python --size enterprise --lang en
  ./generate-firm.sh --dry-run --sector saas --size startup

EOF
}

# ── parse args ───────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sector)  SECTOR="$2";    shift 2 ;;
    --stack)   STACK="$2";     shift 2 ;;
    --size)    SIZE="$2";      shift 2 ;;
    --output)  OUTPUT_DIR="$2"; shift 2 ;;
    --lang)    LANG="$2";      shift 2 ;;
    --dry-run) DRY_RUN=true;   shift 1 ;;
    --force)   FORCE=true;     shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) error "Option inconnue: $1 (voir --help)" ;;
  esac
done

# ── validations ──────────────────────────────────────────────
VALID_SECTORS="generic legal medtech ecommerce fintech saas manufacturing education realestate logistics media automotive energy hr consulting"
VALID_STACKS="typescript python java dotnet go rust mixed"
VALID_SIZES="startup scaleup enterprise"

# ── bash 3.2 compat: capitalize first letter ────────────────
ucfirst() { echo "$1" | awk '{print toupper(substr($0,1,1)) substr($0,2)}'; }

echo "$VALID_SECTORS" | grep -qw "$SECTOR" || error "Secteur invalide: $SECTOR"
echo "$VALID_STACKS"  | grep -qw "$STACK"  || error "Stack invalide: $STACK"
echo "$VALID_SIZES"   | grep -qw "$SIZE"   || error "Taille invalide: $SIZE"

# ── configuration selon taille ───────────────────────────────
case "$SIZE" in
  startup)    DEPTS=("strategy" "engineering" "quality" "operations") ;;
  scaleup)    DEPTS=("strategy" "research_development" "engineering" "quality" "marketing" "support_clients" "operations" "finance") ;;
  enterprise) DEPTS=("strategy" "research_development" "planning_orchestration" "memory" "engineering" "quality" "operations" "support_team" "commercial" "marketing" "support_clients" "finance" "legal" "ra") ;;
esac

# ── utilitaires ──────────────────────────────────────────────
slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' _' '-' | sed 's/[^a-z0-9-]//g'
}

dept_label() {
  case "$1" in
    strategy)              echo "Department Strategy" ;;
    research_development)  echo "Department Research Development" ;;
    planning_orchestration)echo "Department Planning Orchestration" ;;
    memory)                echo "Department Memory" ;;
    engineering)           echo "Department Engineering" ;;
    quality)               echo "Department Quality" ;;
    operations)            echo "Department Operations" ;;
    support_team)          echo "Department Support Team" ;;
    commercial)            echo "Department Commercial" ;;
    marketing)             echo "Department Marketing" ;;
    support_clients)       echo "Department Support Clients" ;;
    finance)               echo "Department Finance" ;;
    legal)                 echo "Department Legal" ;;
    ra)                    echo "Department RA" ;;
    *) echo "Department $1" ;;
  esac
}

dept_services() {
  case "$1" in
    strategy)              echo "planning|architecture|product-discovery|roadmap-prioritization" ;;
    research_development)  echo "research-discovery|rd-prototyping" ;;
    planning_orchestration)echo "workstream-planning|delivery-orchestration" ;;
    memory)                echo "memory-ingestion|memory-retrieval|memory-governance" ;;
    engineering)           echo "backend|frontend|mobile|data-engineering|ai-engineering|integration" ;;
    quality)               echo "testing|security|performance|reliability|accessibility|compliance" ;;
    operations)            echo "documentation|release|devops|sre-incident|support-enablement" ;;
    support_team)          echo "team-support-operations|team-support-tooling" ;;
    commercial)            echo "sales-engineering|revenue-operations|partnerships" ;;
    marketing)             echo "product-marketing|growth-marketing|content-brand" ;;
    support_clients)       echo "client-support-operations|client-incident-response" ;;
    finance)               echo "fpa|pricing-strategy|billing-collections|unit-economics" ;;
    legal)                 echo "contracting|privacy-data|ip-compliance" ;;
    ra)                    echo "agent-recruiting|agent-onboarding|capability-development|governance-performance" ;;
    *) echo "operations" ;;
  esac
}

stack_context() {
  case "$STACK" in
    typescript) echo "TypeScript/Node.js — ESM, strict mode, Zod validation, Vitest" ;;
    python)     echo "Python 3.11+ — type hints, pydantic, pytest, asyncio" ;;
    java)       echo "Java 21 — Spring Boot 3, Maven/Gradle, JUnit 5" ;;
    dotnet)     echo "C# .NET 8 — minimal APIs, xUnit, EF Core" ;;
    go)         echo "Go 1.22 — stdlib-first, table-driven tests, golangci-lint" ;;
    rust)       echo "Rust 1.77 — tokio, serde, cargo test" ;;
    mixed)      echo "Multi-stack — respect existing conventions per service" ;;
  esac
}

sector_context() {
  case "$SECTOR" in
    legal)           echo "Legal services, compliance, contracts, regulatory affairs" ;;
    medtech)         echo "Medical devices, digital health, FDA/CE compliance, clinical workflows" ;;
    ecommerce)       echo "E-commerce, D2C retail, marketplace, catalog management" ;;
    fintech)         echo "Financial services, payments, AML/KYC, regulatory reporting" ;;
    saas)            echo "SaaS product company, B2B/B2C, PLG, subscription model" ;;
    manufacturing)   echo "Industrial manufacturing, supply chain, ERP integration, quality ISO" ;;
    education)       echo "EdTech, LMS, curriculum development, accessibility WCAG" ;;
    realestate)      echo "Real estate, proptech, property management, listing platforms" ;;
    logistics)       echo "Logistics, last-mile delivery, route optimisation, tracking" ;;
    media)           echo "Media, publishing, content production, rights management" ;;
    automotive)      echo "Automotive, connected vehicles, MISRA compliance, OTA updates" ;;
    energy)          echo "Energy, utilities, smart grid, IoT sensors, SCADA integration" ;;
    hr)              echo "HR tech, talent acquisition, people analytics, HRIS integration" ;;
    consulting)      echo "Consulting, client delivery, knowledge management, proposals" ;;
    generic)         echo "General purpose — adapt to any domain" ;;
  esac
}

write_file() {
  local path="$1"
  local content="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    info "[dry-run] Would write: $path"
    return
  fi
  local dir
  dir="$(dirname "$path")"
  mkdir -p "$dir"
  if [[ -f "$path" && "$FORCE" == "false" ]]; then
    warn "Skipping existing file (use --force to overwrite): $path"
    return
  fi
  printf '%s' "$content" > "$path"
  success "Written: ${path#"$OUTPUT_DIR/"}"
}

# ── header ───────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         firm-factory v1.0.0              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""
info "Sector:  $SECTOR ($(sector_context))"
info "Stack:   $STACK ($(stack_context))"
info "Size:    $SIZE (${#DEPTS[@]} departments)"
info "Output:  $OUTPUT_DIR"
info "Lang:    $LANG"
[[ "$DRY_RUN" == "true" ]] && warn "DRY RUN — no files will be written"
echo ""

# ── 1. Create CEO agent ──────────────────────────────────────
DEPTS_LIST=$(printf '"%s", ' "${DEPTS[@]}")
DEPTS_LIST="${DEPTS_LIST%, }"

CEO_CONTENT="---
name: Firm CEO
description: >
  Orchestrateur principal de la firm ${SECTOR} (${SIZE}).
  Reçoit un objectif, le décompose, délègue aux départements actifs,
  collecte les résultats, fusionne et livre le livrable final.
  Utilise firm-orchestration pour le protocole A2A.

  Stack: $(stack_context)
  Secteur: $(sector_context)
---

# Firm CEO — $(ucfirst "$SECTOR") / $(ucfirst "$SIZE")

## Rôle

Tu es le CEO de la firm. Tu orchestres l'ensemble de la pyramide d'agents.

## Départements disponibles pour cette firm (${SIZE})

$(for dept in "${DEPTS[@]}"; do
  echo "- **$(dept_label "$dept")** — services: $(dept_services "$dept" | tr '|' ', ')"
done)

## Protocole de délégation (A2A)

1. Analyse l'objectif reçu et identifie les départements concernés
2. Pour chaque département pertinent, émets un payload de délégation :
   - \`from\`: \"ceo\"
   - \`to\`: \"department:{dept_name}\"  
   - \`objective\`: objectif spécifique du département
   - \`constraints\`: contraintes héritées + contraintes département
   - \`definition_of_done\`: critère d'acceptation mesurable
   - \`context_ref\`: \"memory:delivery/latest\" (si mémoire disponible)
   - \`reply_session\`: \"main\"
3. Collecte tous les résultats via sessions_history (deadline: 30s)
4. Fusionne en respectant l'ordre de dépendance : Strategy → Engineering → Quality → Ops
5. Formate selon le \`delivery_format\` demandé
6. Si firm-delivery-export est installé, déclenche l'export automatiquement

## Sécurité

- Ne jamais modifier des fichiers de production sans confirmation explicite
- Toute action destructive ou difficilement réversible nécessite une confirmation
- Maximum 20 sessions enfants par run d'orchestration
- Timeout global : 5 minutes par run complet

## Pratiques de travail obligatoires

Ces règles s'appliquent à **chaque tâche**, sans exception.
*(Source : Anthropic — \"How Anthropic teams use Claude Code\")*

### Délégation parallèle
- Déléguer en parallèle à tous les départements pertinents simultanément — jamais séquentiellement
- Chaque département maintient son contexte complet — pas de répétition de contexte
- Synchroniser les résultats après deadline de convergence (30s)

### Cycle auto-accept
- Déléguer l'intégralité d'une feature à Engineering sans micro-management
- Laisser Engineering itérer : écrire → tester → corriger → recommencer en autonomie
- Reviewer la solution à ~80 % d'avancement, puis valider les 20 % finaux avant livraison

### Git et checkpoints
- Toute mission commence sur une branche dédiée : \`feat/<slug>\` — jamais sur \`main\`
- Demander des commits checkpoint toutes les 30–50 lignes de code généré
- Toute PR produite en **draft** avec label \`needs-review\` — jamais auto-merge

### Débogage par preuves
- Exiger stack traces ou captures d'écran avant de diagnostiquer
- Tracer le flux de contrôle dans le codebase AVANT de proposer un fix
- Livrer des commandes exactes à exécuter — pas des diagnostics généraux

### Onboarding codebase
- Lire \`AGENTS.md\`, \`README.md\` en priorité absolue avant chaque mission
- Identifier les fichiers pertinents AVANT d'éditer quoi que ce soit

### Documentation de fin de mission
Après chaque mission complétée, produire :
1. Résumé de ce qui a été accompli (1 paragraphe max)
2. Décisions d'architecture prises
3. Améliorations suggérées pour la prochaine mission

### Outputs AI
Tout livrable généré porte la mention obligatoire :
> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation

## Stack tech

$(stack_context)

## Contexte secteur

$(sector_context)
"

write_file "$OUTPUT_DIR/.github/agents/firm-ceo.agent.md" "$CEO_CONTENT"

# ── 2. Create department agents ───────────────────────────────
for dept in "${DEPTS[@]}"; do
  LABEL="$(dept_label "$dept")"
  SERVICES_RAW="$(dept_services "$dept")"
  IFS='|' read -ra SERVICES <<< "$SERVICES_RAW"

  SERVICES_BULLETS=$(for svc in "${SERVICES[@]}"; do
    echo "- ${svc//-/ } service"
  done)

  DEPT_CONTENT="---
name: ${LABEL}
description: >
  Chef de département ${dept//_/ } pour la firm ${SECTOR} (${SIZE}).
  Reçoit la délégation du CEO, décompose en services, coordonne les agents employés,
  collecte les résultats et retourne un rapport synthétique au CEO.
---

# ${LABEL}

## Rôle

Tu es le chef du département ${dept//_/ }. Tu reçois des objectifs du CEO et les délègues
aux services de ton département.

## Services disponibles

${SERVICES_BULLETS}

## Protocole de réception (depuis CEO)

Quand tu reçois un payload via sessions_send, extrais :
- \`objective\` → décompose en tâches service par service
- \`constraints\` → propages à tous les services
- \`definition_of_done\` → adapte par service avec critères mesurables
- \`reply_session\` → utilise pour le rapport de retour

## Protocole de délégation (vers services)

Pour chaque service pertinent :
1. Émets: from=\`dept:${dept}\`, to=\`service:{service_name}\`
2. Objectif service : spécifique et actionnable
3. Contraintes : héritées + contraintes département
4. DoD service : subset mesurable du DoD global

## Rapport de retour (vers CEO)

Format attendu :
\`\`\`json
{
  \"department\": \"${dept}\",
  \"status\": \"done | partial | error\",
  \"services_completed\": [...],
  \"deliverables\": [...],
  \"blockers\": [...],
  \"recommendations\": [...]
}
\`\`\`

## Pratiques de travail obligatoires

### Délégation aux services
- Déléguer en parallèle à tous les services pertinents — jamais séquentiellement
- Chaque service reçoit un objectif spécifique et mesurable (pas de \"voir avec le service\")
- Timeout par service : 20s — escalader au CEO si dépassé

### Qualité des livrables
- Tester/valider la sortie de chaque service AVANT de consolider le rapport département
- Signaler immédiatement tout bloqueur avec une alternative proposée
- Ne jamais marquer \`status: done\` sans avoir vérifié le critère DoD

### Git / PR (si Engineering ou DevOps)
- Toute modification de code sur branche dédiée \`feat/<slug>\` — jamais directement sur \`main\`
- PRs créées en **draft** avec label \`needs-review\` — jamais auto-merge
- Tests écrits après l'implémentation de chaque feature (100 % pass avant push)
- Coverage minimum : **80 %** (lignes + branches + fonctions) — 1 test positif + 1 test négatif par tool/fonction

### Débogage (si Security ou Engineering)
- Analyser la stack trace complète AVANT de proposer un fix
- Fournir les commandes exactes à exécuter — pas seulement le diagnostic
- Tracer le flux de contrôle dans le codebase pour localiser la cause racine

### Sécurité avant déploiement (si Engineering ou Security)
- Avant tout push infra : \`openclaw_sandbox_audit\` + \`openclaw_security_scan\` sur les endpoints modifiés
- Si \`severity: CRITICAL\` → bloquer le merge — fix obligatoire avant tout push
- Si Tailscale Funnel actif : vérifier \`openclaw_rate_limit_check\`
- Dépendance beta/frozen → ADR obligatoire via \`firm_adr_generate\` + commit \`docs/decisions/\` avant merge
- Toute décision d'architecture → \`firm_adr_generate\` (format MADR) + commit \`docs/decisions/\`

### Outputs AI
> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation

## Stack / Secteur

Stack: $(stack_context)
Secteur: $(sector_context)
"
  write_file "$OUTPUT_DIR/.github/agents/$(slugify "$LABEL").agent.md" "$DEPT_CONTENT"

  # ── Service agents per department ────────────────────────────
  IFS='|' read -ra SVC_ARRAY <<< "$SERVICES_RAW"
  for svc in "${SVC_ARRAY[@]}"; do
    SVC_LABEL="${svc//-/ }"
    SVC_FILE="$(slugify "${dept}-${svc}")"

    SVC_CONTENT="---
name: ${LABEL} — $(ucfirst "$SVC_LABEL")
description: >
  Agent employé spécialisé dans le service « ${SVC_LABEL} » du département ${dept//_/ }.
  Exécute les tâches assignées, produit des livrables concrets, respecte les contraintes
  et remonte les résultats au chef de département.
---

# ${LABEL} — $(ucfirst "$SVC_LABEL")

## Rôle

Tu es l'agent employé responsable du service **${SVC_LABEL}** dans le département **${dept//_/ }**.

## Responsabilités

- Exécuter les instructions reçues du département de façon précise et mesurable
- Produire des livrables concrets (code, document, analyse, rapport)
- Respecter strictement les contraintes transmises
- Signaler tout bloqueur immédiatement avec une alternative proposée

## Contraintes d'exécution

- Patches minimaux : ne modifier que ce qui est strictement nécessaire
- Validation ciblée : tester/vérifier avant de déclarer \"done\"
- Aucune action destructive sans confirmation explicite
- Respecter la stack : $(stack_context)
- Respecter le contexte secteur : $(sector_context)

## Pratiques de travail obligatoires

### Exécution
- Travailler sur branche dédiée \`feat/<slug>\` — jamais directement sur \`main\`
- Commiter après chaque étape complétée (pas en fin de mission seulement)
- Tester/valider le livrable AVANT de déclarer \`status: done\` au département

### Débogage
- En cas d'erreur : lire la stack trace complète, tracer le flux de contrôle, puis corriger
- Fournir la commande exacte qui résout le problème — pas seulement le diagnostic
- Si une action est ambiguë : proposer l'alternative la plus sûre, ne pas deviner

### Sécurité (si service security, backend, integration ou ai-engineering)
- Avant tout push : \`openclaw_sandbox_audit\` + \`openclaw_security_scan\` sur le code modifié
- Si \`severity: CRITICAL\` → ne pas pousser — remonter au département immédiatement
- Dépendance beta/frozen → ADR obligatoire via \`firm_adr_generate\` avant merge
- Coverage minimum : **80 %** — 1 test positif + 1 test négatif par fonction/tool

### Output
> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation

## Format de livrable

\`\`\`json
{
  \"service\": \"${svc}\",
  \"status\": \"done | partial | blocked\",
  \"deliverable\": \"<contenu ou référence>\",
  \"confidence\": 0.0-1.0,
  \"next_step\": \"<si partial/blocked>\"
}
\`\`\`
"
    write_file "$OUTPUT_DIR/.github/agents/${SVC_FILE}.agent.md" "$SVC_CONTENT"
  done
done

# ── 3. Create firm-delivery prompt ────────────────────────────
PROMPT_CONTENT="---
mode: agent
description: >
  Prompt orchestré pour la firm ${SECTOR} (${SIZE}, stack ${STACK}).
  Lance le CEO avec un objectif, constraints et definition_of_done.
  Le CEO délègue automatiquement aux ${#DEPTS[@]} départements actifs.
---

Tu es le \`Firm CEO\` de cette firm ${SECTOR}.

## Mission

Lance une orchestration complète avec les paramètres suivants :

**Objective**: \${input:objective:Quel est l'objectif principal de cette mission?}

**Departments**: \${input:departments:Départements à impliquer (laisser vide = tous): ex: engineering,quality}

**Constraints**: \${input:constraints:Contraintes à respecter (séparées par ;): ex: read-only;budget €5k}

**Definition of Done**: \${input:dod:Critère d'acceptation mesurable de la mission}

**Delivery format**: \${input:format:Format de livraison (markdown_report|github_pr|jira_ticket|structured_document|project_brief)}

## Instructions

1. Commence par récupérer le contexte mémoire si Memory OS AI est disponible
2. Décompose l'objectif par département selon leur spécialité
3. Délègue en parallèle via sessions_send à chaque département sélectionné
4. Collecte les résultats (timeout: 30s par département)
5. Fusionne en respectant l'ordre: Strategy → Engineering → Quality → Ops → Commercial
6. Formate selon le delivery_format demandé
7. Si firm-delivery-export est installé, déclenche l'export automatiquement
8. Persiste le résultat en mémoire (clé: delivery/latest)
9. Si \`decision_type: architecture\` détecté dans l'objectif → déclencher \`firm_adr_generate\`
   et commiter le résultat dans \`docs/decisions/\` avant de livrer

## Protocole Anthropic (obligatoire)

*Ces pratiques s'appliquent à chaque run, sans exception.*

### Dispatch parallèle — jamais séquentiel
Lance tous les départements simultanément. N'attends **jamais** qu'un département finisse
avant d'en lancer un autre. Stocke tous les reply_session refs dès le dispatch.

### Mode 80/20 — autonome puis review
Délègue 100 % du travail tactique aux départements (~80 % d'avancement).
N'interviens qu'à la convergence pour valider la direction, les edge cases et la sécurité.

### Débogage par preuves — jamais par hypothèse
Si un département remonte une erreur ou un blocker, exige :
1. La stack trace ou le message d'erreur exact
2. Le flux de contrôle tracé (quel module, quelle étape)
3. La commande ou action exacte qui corrige
Refuse tout diagnostic vague ou "ça semble être un problème de...".

### Git checkpoints — état propre obligatoire
Exige de Engineering un commit après chaque sous-tâche complétée.
Toute feature → branche `feat/<slug>`, PR en draft + label `needs-review`.
Jamais de merge direct sur `main`.

### Documentation de fin de run — automatique
Après chaque orchestration complétée, produits automatiquement :
1. Résumé de la mission (1 paragraphe)
2. Décisions d'architecture ou de processus prises
3. Améliorations suggérées pour la prochaine run similaire
4. Disclaimer IA : ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

### Inputs en langage naturel
Accepte les demandes en texte libre. Si des paramètres sont manquants (dates, budgets,
repos, formats), demande-les explicitement avant de déléguer.

## Secteur

$(sector_context)

## Stack

$(stack_context)
"
write_file "$OUTPUT_DIR/.github/prompts/firm-delivery.prompt.md" "$PROMPT_CONTENT"

# ── 4. VS Code settings ───────────────────────────────────────
SETTINGS_CONTENT='{
  "chat.agent.enabled": true,
  "chat.agentFilesLocations": [
    ".github/agents"
  ],
  "github.copilot.chat.agent.runTasks": true,
  "github.copilot.chat.codesearch.enabled": true
}
'
write_file "$OUTPUT_DIR/.vscode/settings.json" "$SETTINGS_CONTENT"

# ── 5. AGENTS.md ──────────────────────────────────────────────
AGENTS_HEADER="# AGENTS.md — Firm $(ucfirst "$SECTOR") (${SIZE}, ${STACK})

This workspace contains a pyramidal VS Code Copilot agent firm.

## Sector: $(ucfirst "$SECTOR")

$(sector_context)

## Stack: $(ucfirst "$STACK")

$(stack_context)

## Active departments (${#DEPTS[@]})

"
AGENTS_DEPTS_LIST=""
for dept in "${DEPTS[@]}"; do
  AGENTS_DEPTS_LIST+="- $(dept_label "$dept") — $(dept_services "$dept" | tr '|' ', ')"$'\n'
done

AGENTS_FOOTER="
## Usage

1. Open VS Code in this folder
2. Ensure \`chat.agent.enabled\` is true
3. In Copilot Chat, select \`Firm CEO\`
4. Run prompt \`firm-delivery\`
5. Fill in objective, constraints and definition_of_done
6. Let the CEO delegate to departments automatically

## Generated by

firm-factory v1.0.0 — sector: ${SECTOR} — size: ${SIZE} — stack: ${STACK}
Date: $(date -u +%Y-%m-%d)
"
write_file "$OUTPUT_DIR/AGENTS.md" "${AGENTS_HEADER}${AGENTS_DEPTS_LIST}${AGENTS_FOOTER}"

# ── 6. CLAUDE.md — pour Claude Code CLI (pas lu par les agents VS Code) ──────
CLAUDE_CONTENT="# CLAUDE.md — Firm $(ucfirst "$SECTOR") (${SIZE}, ${STACK})

> ⚠️ Ce fichier est lu par **Claude Code CLI** (\`claude\` en terminal) — PAS par les agents VS Code Copilot.
> Les pratiques Anthropic sont intégrées directement dans chaque fichier .agent.md.
> Généré automatiquement par firm-factory le $(date +%Y-%m-%d).

---

## ⚠️ RÈGLES OBLIGATOIRES — CHECKLIST AVANT CHAQUE TÂCHE

- [ ] Branche git dédiée : \`git checkout -b feat/<slug>\` (jamais travailler sur \`main\`)
- [ ] Commiters des checkpoints réguliers (toutes les 30-50 lignes de code généré)
- [ ] Pydantic : modèle de validation pour tout nouvel input structuré
- [ ] Tests : 100 % pass avant chaque push (\`python -m pytest tests/ -v\` ou équivalent)
- [ ] Secrets masqués dans les logs (aucun token en clair dans les outputs ni les commits)
- [ ] Output AI marqué : ⚠️ Contenu généré par IA — validation humaine requise
- [ ] CLAUDE.md mis à jour si nouvelle pratique découverte en fin de session

---

## 🏗️ WORKFLOWS ANTHROPIC — PRATIQUES DES ÉQUIPES INTERNES

*(Source : document officiel Anthropic — \"How Anthropic teams use Claude Code\")*

### Prototypage rapide avec auto-accept
Activer \`shift+tab\` (auto-accept) pour les tâches de prototypage.
Laisser Claude itérer : écrire → tester → corriger → recommencer.
Toujours partir d'un état git propre. Reviewer la solution à ~80 % avant de prendre la main.

### Instances parallèles
Ouvrir plusieurs instances Claude Code dans différents modules simultanément.
Chaque instance maintient son contexte complet. Synchroniser les résultats en fin de cycle.

### Prompts en langage naturel (non-développeurs)
Accepter des fichiers texte décrivant un workflow.
Extraire les inputs nécessaires et les demander explicitement.
Produire un output exploitable (PR, ticket, Excel, Markdown) sans intervention manuelle.

### Débogage par stack trace / screenshot
Fournir la stack trace ou capture d'écran complète en contexte.
Tracer le flux de contrôle dans le codebase AVANT de proposer un fix.
Fournir les commandes exactes à exécuter, pas seulement le diagnostic.

### Onboarding dans la codebase
Lire \`CLAUDE.md\`, \`AGENTS.md\`, \`README.md\` en priorité absolue à chaque session.
Identifier les fichiers pertinents avant d'éditer quoi que ce soit.
Expliquer les dépendances des pipelines si demandé.

### Tests et PR automatisés
Écrire les tests après l'implémentation, pas avant (sauf TDD explicite).
Adresser automatiquement les commentaires de PR via GitHub Actions.
Chaque PR créée en **draft** avec label \`needs-review\` — jamais auto-merge sur \`main\`.

### Documentation de fin de session
Après chaque session significative :
1. Résumer ce qui a été accompli (1 paragraphe)
2. Lister les décisions d'architecture prises
3. Proposer des améliorations à ce CLAUDE.md
4. Commiter : \`docs: update CLAUDE.md — <résumé session>\`

---

## 🏢 STRUCTURE DE CETTE FIRM

**Secteur :** ${SECTOR} | **Taille :** ${SIZE} | **Stack :** ${STACK}
**Départements actifs :** ${DEPTS[*]}

\`\`\`
$(basename "$OUTPUT_DIR")/
├── CLAUDE.md                  ← ce fichier (lire en premier)
├── AGENTS.md                  ← carte de routage des agents
├── .github/
│   ├── agents/                ← fichiers .agent.md (CEO + départements)
│   └── prompts/               ← firm-delivery.prompt.md
├── .vscode/settings.json      ← config VS Code Copilot
└── scripts/install-skills.sh  ← installer les skills ClawHub
\`\`\`

---

## 🔧 TOOLS MCP DISPONIBLES (si mcp-openclaw-extensions actif — port 8012)

| Tool | Action |
|------|--------|
| \`firm_export_auto\` | Publier un deliverable (PR / Jira / Linear / Slack / doc) |
| \`firm_gateway_fleet_broadcast\` | Envoyer un message à toutes les instances Gateway |
| \`vs_context_push\` | Synchroniser le contexte VS Code vers OpenClaw |

Vérifier : \`bash mcp-openclaw-extensions/scripts/status.sh\`

---

## 🔑 PHILOSOPHIE

> \"Utilise l'IA aussi agressivement que possible — c'est la seule façon de
> repousser les limites de ce dont les agents sont capables.\" — Anthropic
>
> \"Plus les fichiers CLAUDE.md sont détaillés, plus Claude Code performe bien.\"

Rôle humain = **supervision** + **review** + **architecture**. Délègue le bas niveau.
"
write_file "$OUTPUT_DIR/CLAUDE.md" "$CLAUDE_CONTENT"

# ── 7. OpenClaw skill installer ───────────────────────────────
# Compute optional sector skill line before building string
SECTOR_SKILL_LINE=""
case "$SECTOR" in
  legal)     SECTOR_SKILL_LINE="npx clawhub@latest install firm-legal-pack" ;;
  medtech)   SECTOR_SKILL_LINE="npx clawhub@latest install firm-medtech-pack" ;;
  ecommerce) SECTOR_SKILL_LINE="npx clawhub@latest install firm-ecommerce-pack" ;;
  fintech)   SECTOR_SKILL_LINE="npx clawhub@latest install firm-fintech-pack" ;;
  saas)      SECTOR_SKILL_LINE="npx clawhub@latest install firm-saas-pack" ;;
esac

INSTALL_CONTENT="#!/usr/bin/env bash
# Auto-generated by firm-factory — sector: ${SECTOR}, size: ${SIZE}
set -euo pipefail
echo 'Installing firm skills for ${SECTOR} (${SIZE})...'
npx clawhub@latest install firm-orchestration
npx clawhub@latest install firm-delivery-export
${SECTOR_SKILL_LINE}
echo 'Skills installed. Run: openclaw onboard --install-daemon'
"
write_file "$OUTPUT_DIR/scripts/install-skills.sh" "$INSTALL_CONTENT"
[[ "$DRY_RUN" == "false" ]] && chmod +x "$OUTPUT_DIR/scripts/install-skills.sh" 2>/dev/null || true

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Generation complete!          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
if [[ "$DRY_RUN" == "false" ]]; then
  info "Files generated in: $OUTPUT_DIR"
  info "Departments: ${DEPTS[*]}"
  echo ""
  echo -e "Next steps:"
  echo -e "  ${CYAN}1.${NC} cd $OUTPUT_DIR"
  echo -e "  ${CYAN}2.${NC} bash scripts/install-skills.sh"
  echo -e "  ${CYAN}3.${NC} code .  (open VS Code)"
  echo -e "  ${CYAN}4.${NC} Select 'Firm CEO' in Copilot Chat"
  echo -e "  ${CYAN}5.${NC} Run prompt 'firm-delivery'"
  echo -e "  ${CYAN}6.${NC} Les pratiques Anthropic sont intégrées dans chaque agent (.agent.md)"
fi
echo ""
