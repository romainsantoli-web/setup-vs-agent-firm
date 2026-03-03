/**
 * Firm Ecosystem VS Code Extension
 *
 * Provides commands and views for managing AI agent firms,
 * inter-session Hebbian memory, and MCP tools directly from VS Code.
 *
 * ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
 */

import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as http from 'http';

const execAsync = promisify(exec);

// ── MCP Client ──────────────────────────────────────────────────────────────

let rpcId = 0;

function getMcpUrl(): string {
    return vscode.workspace.getConfiguration('firm').get('mcpServerUrl', 'http://127.0.0.1:8012');
}

async function mcpCall(toolName: string, args: Record<string, unknown> = {}): Promise<unknown> {
    const url = new URL('/mcp', getMcpUrl());
    rpcId++;
    const payload = JSON.stringify({
        jsonrpc: '2.0',
        id: rpcId,
        method: 'tools/call',
        params: { name: toolName, arguments: args },
    });

    return new Promise((resolve, reject) => {
        const req = http.request(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) },
            timeout: 120_000,
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.error) reject(new Error(json.error.message || JSON.stringify(json.error)));
                    else resolve(json.result);
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${data.slice(0, 200)}`));
                }
            });
        });
        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

async function mcpHealth(): Promise<{ status: string; tools: number }> {
    const url = new URL('/health', getMcpUrl());
    return new Promise((resolve, reject) => {
        http.get(url, { timeout: 5000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch { reject(new Error('Invalid health response')); }
            });
        }).on('error', reject);
    });
}

// ── Commands ────────────────────────────────────────────────────────────────

async function firmInit(): Promise<void> {
    const sectors = [
        'generic', 'legal', 'medtech', 'ecommerce', 'fintech', 'saas',
        'manufacturing', 'education', 'realestate', 'logistics',
        'media', 'automotive', 'energy', 'hr', 'consulting',
    ];

    const sector = await vscode.window.showQuickPick(sectors, {
        placeHolder: 'Select industry sector',
        title: 'Firm: Initialize Agent Firm',
    });
    if (!sector) return;

    const sizes = [
        { label: 'startup', description: '4 departments' },
        { label: 'scaleup', description: '8-12 departments' },
        { label: 'enterprise', description: '18 departments' },
    ];
    const size = await vscode.window.showQuickPick(sizes, {
        placeHolder: 'Select firm size',
        title: 'Firm Size',
    });
    if (!size) return;

    const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';

    const terminal = vscode.window.createTerminal('Firm Init');
    terminal.show();
    terminal.sendText(`firm init --sector ${sector} --size ${size.label} --output "${folder}" --force`);
}

async function firmStart(): Promise<void> {
    const terminal = vscode.window.createTerminal('Firm Server');
    terminal.show();
    terminal.sendText('firm start');
    vscode.window.showInformationMessage('Firm: MCP server starting on port 8012...');
}

async function firmStop(): Promise<void> {
    const terminal = vscode.window.createTerminal('Firm Stop');
    terminal.show();
    terminal.sendText('firm stop');
    vscode.window.showInformationMessage('Firm: Servers stopped.');
}

async function firmMemoryDashboard(): Promise<void> {
    try {
        const result = await mcpCall('openclaw_hebbian_status', {});
        const panel = vscode.window.createWebviewPanel(
            'firmMemory',
            'Firm Memory Dashboard',
            vscode.ViewColumn.One,
            { enableScripts: false },
        );
        panel.webview.html = renderMemoryDashboard(result as Record<string, unknown>);
    } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Memory dashboard failed: ${msg}. Is the MCP server running?`);
    }
}

async function firmMemoryExport(): Promise<void> {
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file('firm-memory-export.json'),
        filters: { 'JSON': ['json'] },
        title: 'Export Firm Memory',
    });
    if (!uri) return;

    const terminal = vscode.window.createTerminal('Firm Export');
    terminal.show();
    terminal.sendText(`firm memory export --output "${uri.fsPath}"`);
}

async function firmSecurityScan(): Promise<void> {
    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Running security scan...',
            cancellable: false,
        }, async () => {
            const result = await mcpCall('openclaw_security_scan', {});
            const doc = await vscode.workspace.openTextDocument({
                content: JSON.stringify(result, null, 2),
                language: 'json',
            });
            await vscode.window.showTextDocument(doc);
        });
    } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Security scan failed: ${msg}`);
    }
}

// ── Dashboard HTML ──────────────────────────────────────────────────────────

function renderMemoryDashboard(data: Record<string, unknown>): string {
    const rules = (data as any)?.layer2_rules || [];
    const ruleRows = rules.map((r: any) => {
        const w = r.weight ?? 0;
        const status = w >= 0.8 ? '🟢 strong' : w >= 0.4 ? '🟡 emerging' : w >= 0.1 ? '⚪ weak' : '🔴 atrophy';
        return `<tr><td>${w.toFixed(2)}</td><td>${status}</td><td>${escapeHtml(r.description || '')}</td></tr>`;
    }).join('\n');

    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family, sans-serif); padding: 16px; color: var(--vscode-foreground); background: var(--vscode-editor-background); }
        table { border-collapse: collapse; width: 100%; margin-top: 12px; }
        th, td { padding: 8px 12px; border: 1px solid var(--vscode-panel-border, #444); text-align: left; }
        th { background: var(--vscode-editor-selectionBackground, #264f78); }
        h1 { font-size: 1.4em; }
        .stat { display: inline-block; margin-right: 24px; font-size: 1.1em; }
    </style>
</head>
<body>
    <h1>🧠 Hebbian Memory Dashboard</h1>
    <div>
        <span class="stat"><strong>Rules:</strong> ${rules.length}</span>
        <span class="stat"><strong>Strong (≥0.8):</strong> ${rules.filter((r: any) => (r.weight ?? 0) >= 0.8).length}</span>
        <span class="stat"><strong>Atrophy (<0.1):</strong> ${rules.filter((r: any) => (r.weight ?? 0) < 0.1).length}</span>
    </div>
    <table>
        <thead><tr><th>Weight</th><th>Status</th><th>Rule</th></tr></thead>
        <tbody>${ruleRows || '<tr><td colspan="3">No rules yet — memory will grow as you work.</td></tr>'}</tbody>
    </table>
</body>
</html>`;
}

function escapeHtml(text: string): string {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Tree Views ──────────────────────────────────────────────────────────────

class MemoryTreeProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChange = new vscode.EventEmitter<vscode.TreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChange.event;

    refresh(): void { this._onDidChange.fire(undefined); }

    getTreeItem(element: vscode.TreeItem): vscode.TreeItem { return element; }

    async getChildren(): Promise<vscode.TreeItem[]> {
        try {
            const health = await mcpHealth();
            return [
                new vscode.TreeItem(`Server: ${health.status}`, vscode.TreeItemCollapsibleState.None),
                new vscode.TreeItem(`Tools: ${health.tools}`, vscode.TreeItemCollapsibleState.None),
            ];
        } catch {
            return [new vscode.TreeItem('Server offline — run firm start', vscode.TreeItemCollapsibleState.None)];
        }
    }
}

// ── Extension Lifecycle ─────────────────────────────────────────────────────

export function activate(context: vscode.ExtensionContext): void {
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('firm.init', firmInit),
        vscode.commands.registerCommand('firm.start', firmStart),
        vscode.commands.registerCommand('firm.stop', firmStop),
        vscode.commands.registerCommand('firm.memoryDashboard', firmMemoryDashboard),
        vscode.commands.registerCommand('firm.memoryExport', firmMemoryExport),
        vscode.commands.registerCommand('firm.securityScan', firmSecurityScan),
    );

    // Register tree view
    const memoryTree = new MemoryTreeProvider();
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('firm.memoryView', memoryTree),
    );

    // Status bar item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(brain) Firm';
    statusBar.tooltip = 'Firm Ecosystem — Click for Memory Dashboard';
    statusBar.command = 'firm.memoryDashboard';
    statusBar.show();
    context.subscriptions.push(statusBar);

    console.log('Firm Ecosystem extension activated');
}

export function deactivate(): void {
    console.log('Firm Ecosystem extension deactivated');
}
