#!/usr/bin/env bash
# Apply GitHub topics to all firm-ecosystem repositories.
# Requires: gh CLI authenticated
#
# Usage: bash scripts/apply-github-topics.sh
#
# ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

set -euo pipefail

REPOS=(
    "romainsantoli-web/firm-ecosystem"
    "romainsantoli-web/mcp-openclaw-extensions"
    "romainsantoli-web/Memory-os-ai"
    "romainsantoli-web/setup-vs-agent-firm"
)

# Topics for discoverability (GitHub search + Explore)
COMMON_TOPICS=(
    "ai-agents"
    "mcp"
    "model-context-protocol"
    "hebbian-memory"
    "inter-session-memory"
    "ai-memory"
    "llm"
    "agent-framework"
)

ECOSYSTEM_TOPICS=(
    "${COMMON_TOPICS[@]}"
    "firm-ecosystem"
    "mcp-server"
    "a2a-protocol"
    "langchain"
    "llamaindex"
    "crewai"
)

MEMORY_TOPICS=(
    "${COMMON_TOPICS[@]}"
    "hebbian-learning"
    "sentence-transformers"
    "embedding"
    "vector-search"
    "neuroscience"
)

OPENCLAW_TOPICS=(
    "${COMMON_TOPICS[@]}"
    "mcp-server"
    "security-audit"
    "compliance"
    "pydantic"
)

SETUP_TOPICS=(
    "${COMMON_TOPICS[@]}"
    "ai-firm"
    "agent-orchestration"
    "docker"
    "devcontainer"
)

apply_topics() {
    local repo="$1"
    shift
    local topics=("$@")
    local topics_str
    topics_str=$(printf '%s\n' "${topics[@]}" | sort -u | tr '\n' ',' | sed 's/,$//')

    echo "→ Setting topics on $repo:"
    echo "  ${topics_str}"

    if command -v gh &>/dev/null; then
        # Use gh API to set topics
        local json_array
        json_array=$(printf '%s\n' "${topics[@]}" | sort -u | jq -Rsc 'split("\n") | map(select(. != ""))')
        gh api -X PUT "repos/${repo}/topics" -f "names=${json_array}" --silent 2>/dev/null \
            && echo "  ✓ Done" \
            || echo "  ! Failed (check gh auth status)"
    else
        echo "  ! gh CLI not installed. Install: brew install gh"
        echo "  Manual: https://github.com/${repo}/settings → Topics"
    fi
}

echo "╔════════════════════════════════════════════════╗"
echo "║  Apply GitHub Topics for Discoverability      ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

apply_topics "romainsantoli-web/firm-ecosystem"          "${ECOSYSTEM_TOPICS[@]}"
echo ""
apply_topics "romainsantoli-web/Memory-os-ai"            "${MEMORY_TOPICS[@]}"
echo ""
apply_topics "romainsantoli-web/mcp-openclaw-extensions"  "${OPENCLAW_TOPICS[@]}"
echo ""
apply_topics "romainsantoli-web/setup-vs-agent-firm"      "${SETUP_TOPICS[@]}"

echo ""
echo "Done. Verify at: https://github.com/romainsantoli-web?tab=repositories"
