#!/usr/bin/env python3
"""Fail CI if required OpenClaw security config controls are missing.

Checks enforce the remediation baseline for docs/internal/mcp-config-unified.json:
- channels.telegram.direct.requireTopic == true
- session.maintenance.maxDiskBytes > 0
- session.maintenance.highWaterBytes > 0 and < maxDiskBytes
- gateway.http.securityHeaders.{strictTransportSecurity,xContentTypeOptions,referrerPolicy}
- gateway.rateLimit configured (maxRequestsPerMinute, maxConcurrent)
- hooks.rateLimit configured (maxRequestsPerMinute, maxConcurrent)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CONFIG_PATH = Path("docs/internal/mcp-config-unified.json")


def get_nested(data: dict, *keys: str):
    cur = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def main() -> int:
    errors: list[str] = []

    if not CONFIG_PATH.exists():
        errors.append(f"Missing config file: {CONFIG_PATH}")
        print("❌ OpenClaw security config gate failed")
        for err in errors:
            print(f"- {err}")
        return 1

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("❌ OpenClaw security config gate failed")
        print(f"- Invalid JSON in {CONFIG_PATH}: {exc}")
        return 1

    require_topic = get_nested(config, "channels", "telegram", "direct", "requireTopic")
    if require_topic is not True:
        errors.append("channels.telegram.direct.requireTopic must be true")

    max_disk = get_nested(config, "session", "maintenance", "maxDiskBytes")
    high_water = get_nested(config, "session", "maintenance", "highWaterBytes")
    if not isinstance(max_disk, (int, float)) or max_disk <= 0:
        errors.append("session.maintenance.maxDiskBytes must be a positive number")
    if not isinstance(high_water, (int, float)) or high_water <= 0:
        errors.append("session.maintenance.highWaterBytes must be a positive number")
    if isinstance(max_disk, (int, float)) and isinstance(high_water, (int, float)):
        if high_water >= max_disk:
            errors.append("session.maintenance.highWaterBytes must be lower than maxDiskBytes")

    sec_headers = get_nested(config, "gateway", "http", "securityHeaders")
    if not isinstance(sec_headers, dict):
        errors.append("gateway.http.securityHeaders must be configured")
    else:
        if not sec_headers.get("strictTransportSecurity"):
            errors.append("gateway.http.securityHeaders.strictTransportSecurity is required")
        if sec_headers.get("xContentTypeOptions") != "nosniff":
            errors.append("gateway.http.securityHeaders.xContentTypeOptions must be 'nosniff'")
        if sec_headers.get("referrerPolicy") != "no-referrer":
            errors.append("gateway.http.securityHeaders.referrerPolicy must be 'no-referrer'")

    gateway_rl = get_nested(config, "gateway", "rateLimit")
    if not isinstance(gateway_rl, dict):
        errors.append("gateway.rateLimit must be configured")
    else:
        if not isinstance(gateway_rl.get("maxRequestsPerMinute"), (int, float)):
            errors.append("gateway.rateLimit.maxRequestsPerMinute must be numeric")
        if not isinstance(gateway_rl.get("maxConcurrent"), (int, float)):
            errors.append("gateway.rateLimit.maxConcurrent must be numeric")

    hooks_rl = get_nested(config, "hooks", "rateLimit")
    if not isinstance(hooks_rl, dict):
        errors.append("hooks.rateLimit must be configured")
    else:
        if not isinstance(hooks_rl.get("maxRequestsPerMinute"), (int, float)):
            errors.append("hooks.rateLimit.maxRequestsPerMinute must be numeric")
        if not isinstance(hooks_rl.get("maxConcurrent"), (int, float)):
            errors.append("hooks.rateLimit.maxConcurrent must be numeric")

    if errors:
        print("❌ OpenClaw security config gate failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("✅ OpenClaw security config gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
