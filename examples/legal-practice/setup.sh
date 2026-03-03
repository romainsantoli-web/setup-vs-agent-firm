#!/usr/bin/env bash
# Legal Practice Example — generates an 8-department AI agent firm for a law practice
set -euo pipefail

echo "⚖️  Legal Practice Example"
echo "========================="
echo ""

if ! command -v firm &>/dev/null; then
    echo "Installing firm-cli..."
    pip install firm-cli
fi

FIRM_DIR="$(dirname "$0")/firm-output"
if [ -d "$FIRM_DIR" ]; then
    echo "Firm already generated at $FIRM_DIR"
else
    echo "Generating legal practice firm (8 departments)..."
    firm init \
        --sector legal \
        --stack python \
        --size scaleup \
        --output "$FIRM_DIR"
fi

echo ""
echo "✅ Firm generated at: $FIRM_DIR"
echo ""
echo "Next steps:"
echo "  1. Start the MCP server:  firm start"
echo "  2. Try asking your AI agent:"
echo '     "Review this contract for potential liability clauses"'
echo '     "What are the GDPR requirements for client data retention?"'
echo '     "Draft a legal memo on force majeure in SaaS agreements"'
