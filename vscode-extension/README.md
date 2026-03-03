# Firm Ecosystem — VS Code Extension

VS Code extension for managing AI agent firms directly from your editor.

## Features

- **Firm: Initialize Agent Firm** — Interactive firm generator (15 sectors × 3 sizes)
- **Firm: Start/Stop MCP Server** — Control the MCP server from command palette
- **Firm: Memory Dashboard** — Webview panel showing Hebbian memory weights and status
- **Firm: Export Memory** — Save memory state to portable JSON
- **Firm: Run Security Scan** — Execute 47 security checks and show results

## Activity Bar

The extension adds a "Firm Ecosystem" panel to the activity bar with:
- **Memory Status** — Server health + tool count
- **MCP Tools** — Browse available tools
- **Agent Departments** — View generated departments

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `firm.mcpServerUrl` | `http://127.0.0.1:8012` | MCP server URL |
| `firm.memoryServerUrl` | `http://127.0.0.1:8765` | Memory server URL |
| `firm.autoStart` | `false` | Auto-start server when CLAUDE.md found |

## Development

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

## Publishing

```bash
npm run package   # creates .vsix
vsce publish      # publish to VS Code Marketplace
```

## Requirements

- VS Code 1.90+
- `firm-cli` installed (`pip install firm-cli`)
- MCP server running (`firm start`)

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
