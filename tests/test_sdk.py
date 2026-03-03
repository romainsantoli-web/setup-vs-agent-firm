"""Tests for the Python SDK — unit tests without MCP server.

Tests client construction, convenience methods, and ToolResult dataclass
without needing a running MCP server.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from firm_sdk import FirmClient, FirmAsyncClient, ToolResult


# ── ToolResult ───────────────────────────────────────────────────────────────


def test_tool_result_success():
    r = ToolResult(tool="test_tool", ok=True, data={"count": 5}, elapsed_ms=1.23)
    assert r.ok is True
    assert r.data["count"] == 5
    assert r.error is None
    assert r.elapsed_ms == 1.23


def test_tool_result_failure():
    r = ToolResult(tool="fail_tool", ok=False, error="Connection refused")
    assert r.ok is False
    assert r.error == "Connection refused"
    assert r.data is None


def test_tool_result_defaults():
    r = ToolResult(tool="t", ok=True)
    assert r.data is None
    assert r.error is None
    assert r.elapsed_ms == 0.0


# ── FirmClient construction ─────────────────────────────────────────────────


def test_client_default_url():
    client = FirmClient()
    assert client.base_url == "http://127.0.0.1:8012"
    assert client.auth_token is None
    assert client.timeout == 120.0


def test_client_custom_url():
    client = FirmClient(base_url="http://custom:9999", auth_token="tok", timeout=30.0)
    assert client.base_url == "http://custom:9999"
    assert client.auth_token == "tok"
    assert client.timeout == 30.0


def test_client_headers_without_auth():
    client = FirmClient()
    h = client._headers()
    assert h["Content-Type"] == "application/json"
    assert "Authorization" not in h


def test_client_headers_with_auth():
    client = FirmClient(auth_token="secret-token-123")
    h = client._headers()
    assert h["Authorization"] == "Bearer secret-token-123"


def test_client_rpc_id_increments():
    client = FirmClient()
    assert client._next_id() == 1
    assert client._next_id() == 2
    assert client._next_id() == 3


# ── Convenience methods (verify they call call_tool with correct args) ──────


def test_security_scan_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.security_scan(config_path="/etc/openclaw/config.yaml")
        mock.assert_called_once()
        args = mock.call_args
        assert args[0][0] == "openclaw_security_scan"
        assert args[0][1]["config_path"] == "/etc/openclaw/config.yaml"


def test_memory_status_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.memory_status()
        mock.assert_called_once_with("openclaw_hebbian_status", {})


def test_memory_analyze_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.memory_analyze(since_days=30)
        mock.assert_called_once_with("openclaw_hebbian_analyze", {"since_days": 30})


def test_memory_weight_update_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.memory_weight_update(dry_run=False)
        mock.assert_called_once_with("openclaw_hebbian_weight_update", {"dry_run": False})


def test_fleet_status_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.fleet_status()
        mock.assert_called_once_with("firm_gateway_fleet_status", {})


def test_a2a_discover_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.a2a_discover(url="http://agent.local")
        mock.assert_called_once()
        assert mock.call_args[0][0] == "openclaw_a2a_discovery"
        assert mock.call_args[0][1]["url"] == "http://agent.local"


def test_export_github_pr_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.export_github_pr(title="Test PR", body="automated")
        mock.assert_called_once()
        assert mock.call_args[0][0] == "firm_export_github_pr"
        assert mock.call_args[0][1]["title"] == "Test PR"


def test_compliance_check_calls_correct_tool():
    client = FirmClient()
    with patch.object(client, "call_tool", return_value=ToolResult(tool="t", ok=True)) as mock:
        client.compliance_check(config_path="/path/to/config.yaml")
        mock.assert_called_once()
        assert mock.call_args[0][0] == "openclaw_elicitation_audit"


# ── Error handling (call_tool with mock _rpc) ──────────────────────────────


def test_call_tool_handles_rpc_error():
    client = FirmClient()
    with patch.object(client, "_rpc", return_value={"error": {"code": -1, "message": "not found"}}):
        result = client.call_tool("nonexistent_tool", {})
        assert result.ok is False
        assert "not found" in result.error


def test_call_tool_handles_exception():
    client = FirmClient()
    with patch.object(client, "_rpc", side_effect=ConnectionError("refused")):
        result = client.call_tool("test", {})
        assert result.ok is False
        assert "refused" in result.error
        assert result.elapsed_ms >= 0


def test_call_tool_success():
    client = FirmClient()
    with patch.object(client, "_rpc", return_value={"result": {"status": "ok", "count": 42}}):
        result = client.call_tool("openclaw_hebbian_status", {})
        assert result.ok is True
        assert result.data["count"] == 42
        assert result.elapsed_ms >= 0


# ── FirmAsyncClient construction ─────────────────────────────────────────────


def test_async_client_construction():
    client = FirmAsyncClient()
    assert client.base_url == "http://127.0.0.1:8012"
    assert client.auth_token is None
    assert client.timeout == 120.0


def test_async_client_custom():
    client = FirmAsyncClient(base_url="http://custom:1234", auth_token="abc", timeout=60.0)
    assert client.base_url == "http://custom:1234"
    assert client.auth_token == "abc"


def test_async_client_headers_with_auth():
    client = FirmAsyncClient(auth_token="my-token")
    h = client._headers()
    assert h["Authorization"] == "Bearer my-token"


def test_async_client_rpc_id_increments():
    client = FirmAsyncClient()
    assert client._next_id() == 1
    assert client._next_id() == 2
