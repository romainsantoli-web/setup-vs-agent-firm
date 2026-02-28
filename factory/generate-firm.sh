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

# Firm CEO — ${SECTOR^} / ${size^}

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
name: ${LABEL} — ${SVC_LABEL^}
description: >
  Agent employé spécialisé dans le service « ${SVC_LABEL} » du département ${dept//_/ }.
  Exécute les tâches assignées, produit des livrables concrets, respecte les contraintes
  et remonte les résultats au chef de département.
---

# ${LABEL} — ${SVC_LABEL^}

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
AGENTS_HEADER="# AGENTS.md — Firm ${SECTOR^} (${SIZE}, ${STACK})

This workspace contains a pyramidal VS Code Copilot agent firm.

## Sector: ${SECTOR^}

$(sector_context)

## Stack: ${STACK^}

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

# ── 6. OpenClaw skill installer ───────────────────────────────
INSTALL_CONTENT="#!/usr/bin/env bash
# Auto-generated by firm-factory — sector: ${SECTOR}, size: ${SIZE}
set -euo pipefail
echo 'Installing firm skills for ${SECTOR} (${SIZE})...'
npx clawhub@latest install firm-orchestration
npx clawhub@latest install firm-delivery-export
$(case "$SECTOR" in
  legal)    echo "npx clawhub@latest install firm-legal-pack" ;;
  medtech)  echo "npx clawhub@latest install firm-medtech-pack" ;;
  ecommerce)echo "npx clawhub@latest install firm-ecommerce-pack" ;;
  fintech)  echo "npx clawhub@latest install firm-fintech-pack" ;;
  saas)     echo "npx clawhub@latest install firm-saas-pack" ;;
esac)
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
fi
echo ""
