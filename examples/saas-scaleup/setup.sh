#!/usr/bin/env bash
# SaaS Scale-up Example — generates a 12-department enterprise AI agent firm
set -euo pipefail

echo "🚀 SaaS Scale-up Example"
echo "========================"
echo ""

if ! command -v firm &>/dev/null; then
    echo "Installing firm-cli..."
    pip install firm-cli
fi

FIRM_DIR="$(dirname "$0")/firm-output"
if [ -d "$FIRM_DIR" ]; then
    echo "Firm already generated at $FIRM_DIR"
else
    echo "Generating SaaS scale-up firm (12 departments)..."
    firm init \
        --sector saas \
        --stack fullstack \
        --size scaleup \
        --output "$FIRM_DIR"
fi

echo ""
echo "✅ Firm generated at: $FIRM_DIR"
echo ""
echo "Features demonstrated:"
echo "  • 12 departments with specialized agents"
echo "  • Fleet management (multi-instance Gateway)"
echo "  • Delivery pipeline (GitHub PR / Jira / Slack)"
echo "  • Full security audit suite"
echo "  • Hebbian memory across all departments"
echo ""
echo "Next steps:"
echo "  1. firm start"
echo "  2. firm start --memory    # enable inter-session memory"
echo "  3. firm memory dashboard  # view learned patterns"
