# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 3.x     | ✅ Active  |
| 2.x     | ⚠️ Security fixes only |
| < 2.0   | ❌ End of life |

## Reporting a vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, please email: **security@firm-ecosystem.dev**

Or use [GitHub Security Advisories](https://github.com/romainsantoli-web/firm-ecosystem/security/advisories/new) to report privately.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Impact assessment (what an attacker could do)
- Suggested fix (if you have one)

### Response timeline

- **24h**: Acknowledgment of receipt
- **72h**: Initial assessment and severity rating
- **7 days**: Fix developed and tested
- **14 days**: Security advisory published + patched release

## Security measures in place

### Authentication & authorization
- Timing-safe token comparison (`hmac.compare_digest`)
- Bearer token auth on MCP server
- Minimal CI permissions (`contents: read`, `pull-requests: write`)

### Input validation
- Pydantic v2 models on **all** MCP tool inputs (138+ models)
- Path traversal blocking (`..`) on all file path parameters
- SQL injection guard (regex whitelist on table names)
- Session ID regex: `^[a-zA-Z0-9_\-:.]+$`
- Request body cap: 2MB (`client_max_size`)

### Secret handling
- `mask_secret()` on all log outputs (last 4 chars only)
- `.env` in `.gitignore`
- No hardcoded secrets in source code
- External Secrets lifecycle validation tool

### Runtime protection
- Tool execution timeout: 120s (configurable `TOOL_TIMEOUT_S`)
- WebSocket payload cap: 32KB
- Atomic file writes (rename from `.tmp`)
- `inspect.signature` filtering (no parameter injection)

### Audit tools
47 automated security checks across 10 modules:
- 9 CRITICAL checks (SQL injection, sandbox, secrets, auth bypass)
- 19 HIGH checks (gateway auth, CVE detection, shell env sanitization)
- 19 MEDIUM checks (disk budget, OTEL redaction, rate limiting)

## Responsible disclosure

We follow [coordinated vulnerability disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure). Reporters will be credited in the security advisory unless they prefer anonymity.
