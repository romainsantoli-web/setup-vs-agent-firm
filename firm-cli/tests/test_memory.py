"""Tests for firm memory export/import commands.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import os

from firm_cli.main import cli
from firm_cli.memory import (
    _EXPORT_MAGIC,
    _EXPORT_VERSION,
    _find_claude_md,
    _parse_layer2_rules,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

SAMPLE_CLAUDE_MD = """\
# CLAUDE.md

## Layer 2 — Consolidated Patterns

[0.94] Always run tests before pushing code
[0.87] Use Pydantic for input validation
[0.62] Prefer composition over inheritance
[0.15] Check coverage before merging
[0.03] Alphabetize import groups
"""


def _write_claude_md(tmp_path, content=SAMPLE_CLAUDE_MD):
    """Write a CLAUDE.md and a .git marker so _find_claude_md() stops here."""
    (tmp_path / "CLAUDE.md").write_text(content, encoding="utf-8")
    (tmp_path / ".git").mkdir(exist_ok=True)
    return tmp_path / "CLAUDE.md"


# ── Parse rules ──────────────────────────────────────────────────────────────


def test_parse_layer2_rules(tmp_path):
    claude_md = _write_claude_md(tmp_path)
    rules = _parse_layer2_rules(claude_md)
    assert len(rules) == 5
    # sorted by weight desc
    assert rules[0]["weight"] == 0.94
    assert rules[0]["description"] == "Always run tests before pushing code"
    assert rules[-1]["weight"] == 0.03


def test_parse_layer2_no_rules(tmp_path):
    claude_md = _write_claude_md(tmp_path, "# CLAUDE.md\nNothing here.")
    rules = _parse_layer2_rules(claude_md)
    assert rules == []


# ── Find CLAUDE.md ───────────────────────────────────────────────────────────


def test_find_claude_md_in_cwd(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)
    found = _find_claude_md()
    assert found is not None
    assert found.name == "CLAUDE.md"


def test_find_claude_md_missing(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    found = _find_claude_md()
    assert found is None


# ── Export ───────────────────────────────────────────────────────────────────


def test_export_creates_json(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "export.json"
    ret = cli(["memory", "export", "--output", str(output)])
    assert ret == 0
    assert output.exists()

    data = json.loads(output.read_text())
    assert data["magic"] == _EXPORT_MAGIC
    assert data["version"] == _EXPORT_VERSION
    assert data["memory"]["layer2_count"] == 5
    assert len(data["memory"]["layer2_rules"]) == 5
    assert "claude_md_content" in data
    assert "[0.94]" in data["claude_md_content"]


def test_export_without_claude_md_fails(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    ret = cli(["memory", "export", "--output", str(tmp_path / "out.json")])
    assert ret == 1
    assert not (tmp_path / "out.json").exists()


def test_export_includes_session_data(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    sessions_dir = tmp_path / ".firm" / "sessions"
    sessions_dir.mkdir(parents=True)
    log = sessions_dir / "session-001.jsonl"
    log.write_text('{"event": "tool_call", "tool": "test"}\n')
    monkeypatch.chdir(tmp_path)

    output = tmp_path / "export.json"
    cli(["memory", "export", "--output", str(output)])
    data = json.loads(output.read_text())
    assert data["sessions"]["count"] >= 1
    assert len(data["session_data"]) >= 1
    assert data["session_data"][0]["entries_count"] == 1


# ── Import — full replace ───────────────────────────────────────────────────


def test_import_full_replace(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Export first
    export_path = tmp_path / "export.json"
    cli(["memory", "export", "--output", str(export_path)])

    # Delete the original CLAUDE.md
    os.remove(tmp_path / "CLAUDE.md")

    # Re-import
    ret = cli(["memory", "import", str(export_path)])
    assert ret == 0

    # CLAUDE.md should be restored
    restored = (tmp_path / "CLAUDE.md").read_text()
    assert "[0.94]" in restored
    assert "Always run tests" in restored


def test_import_creates_backup(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Export
    export_path = tmp_path / "export.json"
    cli(["memory", "export", "--output", str(export_path)])

    # Import over existing — should create .bak
    cli(["memory", "import", str(export_path)])
    assert (tmp_path / "CLAUDE.md.bak").exists()


def test_import_nonexistent_file(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)
    ret = cli(["memory", "import", "/no/such/file.json"])
    assert ret == 1


def test_import_invalid_json(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json at all")
    ret = cli(["memory", "import", str(bad_file)])
    assert ret == 1


def test_import_wrong_magic(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps({"magic": "wrong", "version": "1.0.0"}))
    ret = cli(["memory", "import", str(bad_file)])
    assert ret == 1


# ── Import — merge mode ─────────────────────────────────────────────────────


def test_import_merge_adds_new_rules(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Create an export with extra rules
    export_data = {
        "magic": _EXPORT_MAGIC,
        "version": _EXPORT_VERSION,
        "memory": {
            "layer2_rules": [
                {"weight": 0.94, "description": "Always run tests before pushing code"},  # exists
                {"weight": 0.75, "description": "Brand new rule from another project"},  # new
            ],
            "layer2_count": 2,
        },
        "claude_md_content": "",
        "sessions": {"count": 0, "paths": []},
        "session_data": [],
    }
    export_path = tmp_path / "other.json"
    export_path.write_text(json.dumps(export_data))

    ret = cli(["memory", "import", str(export_path), "--merge"])
    assert ret == 0

    # Check the new rule was appended
    content = (tmp_path / "CLAUDE.md").read_text()
    assert "Brand new rule" in content
    # Original rules still present
    assert "[0.94] Always run tests" in content


def test_import_merge_skip_duplicates(tmp_path, monkeypatch):
    _write_claude_md(tmp_path)
    monkeypatch.chdir(tmp_path)

    export_data = {
        "magic": _EXPORT_MAGIC,
        "version": _EXPORT_VERSION,
        "memory": {
            "layer2_rules": [
                {"weight": 0.94, "description": "Always run tests before pushing code"},
            ],
            "layer2_count": 1,
        },
        "claude_md_content": "",
        "sessions": {"count": 0, "paths": []},
        "session_data": [],
    }
    export_path = tmp_path / "same.json"
    export_path.write_text(json.dumps(export_data))

    ret = cli(["memory", "import", str(export_path), "--merge"])
    assert ret == 0

    # No backup created since no changes (or backup exists from merge logic)
    # Content should remain unchanged
    content = (tmp_path / "CLAUDE.md").read_text()
    assert content.count("Always run tests") == 1


def test_import_session_logs(tmp_path, monkeypatch):
    """Import restores session JSONL files to .firm/sessions/."""
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)

    export_data = {
        "magic": _EXPORT_MAGIC,
        "version": _EXPORT_VERSION,
        "memory": {"layer2_rules": [], "layer2_count": 0},
        "claude_md_content": "# Fresh CLAUDE.md\n",
        "sessions": {"count": 1, "paths": ["/old/session-001.jsonl"]},
        "session_data": [
            {
                "path": "/old/session-001.jsonl",
                "entries_count": 2,
                "entries": [
                    {"event": "tool_call", "tool": "test"},
                    {"event": "result", "ok": True},
                ],
            }
        ],
    }
    export_path = tmp_path / "with-sessions.json"
    export_path.write_text(json.dumps(export_data))

    ret = cli(["memory", "import", str(export_path)])
    assert ret == 0

    session_file = tmp_path / ".firm" / "sessions" / "session-001.jsonl"
    assert session_file.exists()
    lines = session_file.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["event"] == "tool_call"
