#!/usr/bin/env bash
# Fintech Startup Example — generates and starts a complete AI agent firm
set -euo pipefail

echo "🏦 Fintech Startup Example"
echo "========================="
echo ""

# Check prerequisites
if ! command -v firm &>/dev/null; then
    echo "Installing firm-cli..."
    pip install firm-cli
fi

# Generate the firm
FIRM_DIR="$(dirname "$0")/firm-output"
if [ -d "$FIRM_DIR" ]; then
    echo "Firm already generated at $FIRM_DIR"
else
    echo "Generating fintech startup firm..."
    firm init \
        --sector fintech \
        --stack typescript \
        --size startup \
        --output "$FIRM_DIR"
fi

echo ""
echo "✅ Firm generated at: $FIRM_DIR"
echo ""
echo "Next steps:"
echo "  1. Start the MCP server:  firm start"
echo "  2. Add to VS Code settings.json:"
echo '     "mcp.servers": { "firm": { "url": "http://127.0.0.1:8012/mcp" } }'
echo "  3. Try asking your AI agent:"
echo '     "Run a security audit on my OpenClaw config"'
echo '     "What are the AML/KYC compliance requirements for a neobank?"'
echo '     "Generate an architecture decision record for our auth system"'
echo ""
echo "📖 See README.md for more details."
