"""Tests for firm start --split and firm status --watch features.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from firm_cli.server import (
    SPLIT_DOMAINS,
    _build_status_table,
    _health_check,
    _heartbeat_check,
    _is_running,
    run_start,
    run_status,
    run_stop,
)


# ── Split domain definitions ────────────────────────────────────────────────


def test_split_domains_exist():
    """Three domains are defined: security, memory, business."""
    assert set(SPLIT_DOMAINS.keys()) == {"security", "memory", "business"}


def test_split_domains_have_required_keys():
    """Each domain has port, pidfile, modules, description."""
    for domain, info in SPLIT_DOMAINS.items():
        assert "port" in info, f"{domain} missing port"
        assert "pidfile" in info, f"{domain} missing pidfile"
        assert "modules" in info, f"{domain} missing modules"
        assert "description" in info, f"{domain} missing description"
        assert isinstance(info["modules"], list)
        assert len(info["modules"]) > 0


def test_split_domains_unique_ports():
    """Each domain has a unique port."""
    ports = [info["port"] for info in SPLIT_DOMAINS.values()]
    assert len(ports) == len(set(ports))


def test_split_domain_ports():
    """Ports are 8012, 8013, 8014."""
    ports = sorted(info["port"] for info in SPLIT_DOMAINS.values())
    assert ports == [8012, 8013, 8014]


# ── run_start with --split ──────────────────────────────────────────────────


def test_run_start_unified_mode():
    """run_start without --split starts in unified mode."""
    args = argparse.Namespace(split=False)
    with patch("firm_cli.server._run_start_unified", return_value=0) as mock:
        ret = run_start(args)
        assert ret == 0
        mock.assert_called_once()


def test_run_start_split_mode():
    """run_start with --split starts in split mode."""
    args = argparse.Namespace(split=True)
    with patch("firm_cli.server._run_start_split", return_value=0) as mock:
        ret = run_start(args)
        assert ret == 0
        mock.assert_called_once()


def test_run_start_no_split_attr():
    """run_start without split attribute defaults to unified."""
    args = argparse.Namespace()
    with patch("firm_cli.server._run_start_unified", return_value=0) as mock:
        ret = run_start(args)
        assert ret == 0
        mock.assert_called_once()


# ── run_stop cleans split PIDs ──────────────────────────────────────────────


def test_run_stop_handles_split_and_unified(tmp_path):
    """run_stop cleans up both unified and split-mode pidfiles."""
    with patch("firm_cli.server.PIDFILE_DIR", tmp_path), \
         patch("firm_cli.server.OPENCLAW_PID", tmp_path / "oc.pid"), \
         patch("firm_cli.server.MEMORY_PID", tmp_path / "mem.pid"):
        # Patch split domain pidfiles
        for domain, info in SPLIT_DOMAINS.items():
            info_copy = dict(info)
            info_copy["pidfile"] = tmp_path / f"{domain}.pid"
            SPLIT_DOMAINS[domain] = info_copy
        ret = run_stop()
        assert ret == 0


# ── _is_running ─────────────────────────────────────────────────────────────


def test_is_running_no_pidfile(tmp_path):
    pidfile = tmp_path / "test.pid"
    alive, pid = _is_running(pidfile)
    assert alive is False
    assert pid is None


def test_is_running_stale_pid(tmp_path):
    pidfile = tmp_path / "test.pid"
    pidfile.write_text("999999999")  # PID that doesn't exist
    alive, pid = _is_running(pidfile)
    assert alive is False
    assert pid is None


def test_is_running_invalid_pid(tmp_path):
    pidfile = tmp_path / "test.pid"
    pidfile.write_text("not_a_number")
    alive, pid = _is_running(pidfile)
    assert alive is False


# ── _health_check ────────────────────────────────────────────────────────────


def test_health_check_unreachable():
    """Health check returns None for unreachable endpoint."""
    result = _health_check("http://127.0.0.1:19999/nonexistent")
    assert result is None


# ── _heartbeat_check ─────────────────────────────────────────────────────────


def test_heartbeat_check_empty():
    results = _heartbeat_check([])
    assert results == []


def test_heartbeat_check_unreachable():
    results = _heartbeat_check([("test", "http://127.0.0.1:19999/health")])
    assert len(results) == 1
    assert results[0]["name"] == "test"
    assert results[0]["alive"] is False


# ── _build_status_table ─────────────────────────────────────────────────────


def test_build_status_table_returns_table():
    table = _build_status_table()
    assert table is not None
    # Should have columns: Component, Status, PID, Endpoint, Heartbeat, Details
    assert len(table.columns) == 6


# ── run_status ───────────────────────────────────────────────────────────────


def test_run_status_no_watch():
    """run_status without watch returns immediately."""
    ret = run_status(watch=False)
    assert ret == 0


def test_run_status_watch_keyboard_interrupt():
    """run_status with watch stops on KeyboardInterrupt."""
    with patch("firm_cli.server.Live") as mock_live:
        mock_live.return_value.__enter__ = MagicMock()
        mock_live.return_value.__exit__ = MagicMock(return_value=False)
        # Make time.sleep raise KeyboardInterrupt
        with patch("firm_cli.server.time.sleep", side_effect=KeyboardInterrupt):
            ret = run_status(watch=True, interval=1)
            assert ret == 0


# ── CLI integration ──────────────────────────────────────────────────────────


def test_cli_status_watch_flag():
    """firm status --watch parses correctly."""
    from firm_cli.main import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["status", "--watch"])
    assert args.watch is True
    assert args.interval == 5


def test_cli_status_interval_flag():
    """firm status --watch --interval 10 parses correctly."""
    from firm_cli.main import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["status", "--watch", "--interval", "10"])
    assert args.watch is True
    assert args.interval == 10


def test_cli_start_split_flag():
    """firm start --split parses correctly."""
    from firm_cli.main import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["start", "--split"])
    assert args.split is True


def test_cli_start_no_split():
    """firm start without --split defaults to False."""
    from firm_cli.main import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["start"])
    assert args.split is False
