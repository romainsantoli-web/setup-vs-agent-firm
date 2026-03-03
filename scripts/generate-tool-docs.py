#!/usr/bin/env python3
"""Generate tool reference documentation from MCP server source code.

Reads the TOOL_REGISTRY from mcp-openclaw-extensions and produces:
- docs/TOOLS.md — complete tool reference grouped by category
- docs/TOOLS-SUMMARY.md — one-line-per-tool quick reference
"""

import importlib
import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "mcp-openclaw-extensions" / "src"
sys.path.insert(0, str(SRC.parent))

DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)


def load_registry() -> dict:
    """Import main module and return TOOL_REGISTRY."""
    # We need to import the src package
    sys.path.insert(0, str(SRC.parent))
    from src.main import TOOL_REGISTRY, __version__
    return TOOL_REGISTRY, __version__


def generate_docs():
    """Generate Markdown documentation from TOOL_REGISTRY."""
    registry, version = load_registry()

    # Group by category
    by_category: dict[str, list] = defaultdict(list)
    for name, tool in sorted(registry.items()):
        cat = tool.get("category", "uncategorized")
        by_category[cat].append(tool)

    # --- TOOLS.md (full reference) ---
    lines = [
        f"# MCP Tool Reference — v{version}",
        "",
        f"> Auto-generated from source code. {len(registry)} tools across {len(by_category)} categories.",
        "",
        "---",
        "",
    ]

    # Table of contents
    lines.append("## Categories\n")
    for cat in sorted(by_category.keys()):
        tools = by_category[cat]
        lines.append(f"- [{cat}](#{cat.replace(' ', '-').lower()}) ({len(tools)} tools)")
    lines.append("")

    # Each category
    for cat in sorted(by_category.keys()):
        tools = by_category[cat]
        lines.append(f"---\n\n## {cat}\n")

        for tool in sorted(tools, key=lambda t: t["name"]):
            name = tool["name"]
            desc = tool.get("description", "No description")
            schema = tool.get("inputSchema", {})
            props = schema.get("properties", {})
            required = set(schema.get("required", []))

            lines.append(f"### `{name}`\n")
            lines.append(f"{desc}\n")

            if props:
                lines.append("| Parameter | Type | Required | Description |")
                lines.append("|-----------|------|----------|-------------|")
                for pname, pinfo in sorted(props.items()):
                    ptype = pinfo.get("type", "any")
                    pdesc = pinfo.get("description", "—")
                    req = "✅" if pname in required else "—"
                    lines.append(f"| `{pname}` | {ptype} | {req} | {pdesc} |")
                lines.append("")

    full_ref = "\n".join(lines) + "\n"
    (DOCS / "TOOLS.md").write_text(full_ref)
    print(f"✅ docs/TOOLS.md — {len(registry)} tools, {len(full_ref)} bytes")

    # --- TOOLS-SUMMARY.md (quick reference) ---
    summary_lines = [
        f"# Tool Summary — v{version}",
        "",
        f"{len(registry)} tools across {len(by_category)} categories.",
        "",
        "| Tool | Category | Description |",
        "|------|----------|-------------|",
    ]
    for name, tool in sorted(registry.items()):
        cat = tool.get("category", "—")
        desc = tool.get("description", "—")
        # Truncate long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        summary_lines.append(f"| `{name}` | {cat} | {desc} |")

    summary = "\n".join(summary_lines) + "\n"
    (DOCS / "TOOLS-SUMMARY.md").write_text(summary)
    print(f"✅ docs/TOOLS-SUMMARY.md — {len(registry)} tools, {len(summary)} bytes")


if __name__ == "__main__":
    generate_docs()
