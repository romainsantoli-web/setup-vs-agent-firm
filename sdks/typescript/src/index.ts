/**
 * firm-sdk — TypeScript client for the Firm Ecosystem MCP server.
 *
 * @example
 * ```ts
 * import { FirmClient } from "firm-sdk";
 *
 * const client = new FirmClient();
 * const health = await client.health();
 * const result = await client.callTool("openclaw_hebbian_status", {});
 * ```
 *
 * ⚠️ AI-generated content — human validation required before use.
 */

export interface ToolResult {
  tool: string;
  ok: boolean;
  data?: unknown;
  error?: string;
  elapsedMs: number;
}

export interface FirmClientOptions {
  baseUrl?: string;
  authToken?: string;
  timeout?: number;
}

export class FirmClient {
  private baseUrl: string;
  private authToken?: string;
  private timeout: number;
  private rpcId = 0;

  constructor(options: FirmClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? "http://127.0.0.1:8012";
    this.authToken = options.authToken;
    this.timeout = options.timeout ?? 120_000;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.authToken) {
      h["Authorization"] = `Bearer ${this.authToken}`;
    }
    return h;
  }

  private nextId(): number {
    return ++this.rpcId;
  }

  /** Check server health */
  async health(): Promise<Record<string, unknown>> {
    const resp = await fetch(`${this.baseUrl}/health`, {
      headers: this.headers(),
      signal: AbortSignal.timeout(5000),
    });
    return resp.json() as Promise<Record<string, unknown>>;
  }

  /** List all available MCP tools */
  async listTools(): Promise<Array<Record<string, unknown>>> {
    const result = await this.rpc("tools/list", {});
    return (result as Record<string, unknown>)["tools"] as Array<Record<string, unknown>> ?? [];
  }

  /** Call an MCP tool by name */
  async callTool(name: string, args: Record<string, unknown> = {}): Promise<ToolResult> {
    const start = performance.now();
    try {
      const result = await this.rpc("tools/call", { name, arguments: args });
      const elapsed = performance.now() - start;
      const r = result as Record<string, unknown>;
      if (r["error"]) {
        return { tool: name, ok: false, error: String(r["error"]), elapsedMs: elapsed };
      }
      return { tool: name, ok: true, data: r["result"], elapsedMs: elapsed };
    } catch (e) {
      const elapsed = performance.now() - start;
      return { tool: name, ok: false, error: String(e), elapsedMs: elapsed };
    }
  }

  private async rpc(method: string, params: Record<string, unknown>): Promise<unknown> {
    const body = JSON.stringify({
      jsonrpc: "2.0",
      id: this.nextId(),
      method,
      params,
    });
    const resp = await fetch(`${this.baseUrl}/mcp`, {
      method: "POST",
      headers: this.headers(),
      body,
      signal: AbortSignal.timeout(this.timeout),
    });
    return resp.json();
  }

  // ── Convenience methods ──────────────────────────────────────────────

  /** Run a security scan */
  async securityScan(configPath = ""): Promise<ToolResult> {
    return this.callTool("openclaw_security_scan", { config_path: configPath });
  }

  /** Get Hebbian memory status */
  async memoryStatus(): Promise<ToolResult> {
    return this.callTool("openclaw_hebbian_status", {});
  }

  /** Run Hebbian analysis */
  async memoryAnalyze(sinceDays = 90): Promise<ToolResult> {
    return this.callTool("openclaw_hebbian_analyze", { since_days: sinceDays });
  }

  /** Update Hebbian weights */
  async memoryWeightUpdate(dryRun = true): Promise<ToolResult> {
    return this.callTool("openclaw_hebbian_weight_update", { dry_run: dryRun });
  }

  /** Get fleet status */
  async fleetStatus(): Promise<ToolResult> {
    return this.callTool("firm_gateway_fleet_status", {});
  }

  /** Discover A2A agents */
  async a2aDiscover(url = ""): Promise<ToolResult> {
    return this.callTool("openclaw_a2a_discovery", { url });
  }

  /** Export as GitHub PR */
  async exportGithubPr(args: Record<string, unknown> = {}): Promise<ToolResult> {
    return this.callTool("firm_export_github_pr", args);
  }

  /** Post digest to Slack */
  async exportSlack(args: Record<string, unknown> = {}): Promise<ToolResult> {
    return this.callTool("firm_export_slack_digest", args);
  }
}
