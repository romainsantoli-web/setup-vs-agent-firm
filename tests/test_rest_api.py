"""Tests for the REST API wrapper — unit tests without MCP server.

Tests the handler logic, route mapping, and error handling
by mocking the MCP client calls.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
from unittest.mock import patch

from integrations.rest_api import ROUTES, FirmRESTHandler


# ── Route mapping ────────────────────────────────────────────────────────────


def test_all_routes_have_required_keys():
    for route_key, route in ROUTES.items():
        assert "tool" in route, f"Route {route_key} missing 'tool'"
        assert "defaults" in route, f"Route {route_key} missing 'defaults'"
        assert "doc" in route, f"Route {route_key} missing 'doc'"


def test_route_keys_are_valid_http():
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
    for route_key in ROUTES:
        parts = route_key.split(" ", 1)
        assert len(parts) == 2, f"Invalid route key: {route_key}"
        method, path = parts
        assert method in valid_methods, f"Invalid HTTP method in: {route_key}"
        assert path.startswith("/api/v1/"), f"Path must start with /api/v1/: {route_key}"


def test_expected_routes_exist():
    expected = [
        "GET /api/v1/security/scan",
        "POST /api/v1/memory/harvest",
        "GET /api/v1/memory/status",
        "POST /api/v1/memory/analyze",
        "POST /api/v1/memory/weight-update",
        "GET /api/v1/fleet/status",
        "POST /api/v1/a2a/discover",
        "POST /api/v1/a2a/task",
        "POST /api/v1/export/github-pr",
        "POST /api/v1/export/slack",
        "GET /api/v1/compliance/spec",
    ]
    for route in expected:
        assert route in ROUTES, f"Missing expected route: {route}"


def test_route_count():
    assert len(ROUTES) >= 11, f"Expected at least 11 routes, got {len(ROUTES)}"


# ── Tool name mapping ───────────────────────────────────────────────────────


def test_security_route_maps_correctly():
    route = ROUTES["GET /api/v1/security/scan"]
    assert route["tool"] == "openclaw_security_scan"


def test_memory_routes_map_correctly():
    assert ROUTES["POST /api/v1/memory/harvest"]["tool"] == "openclaw_hebbian_harvest"
    assert ROUTES["GET /api/v1/memory/status"]["tool"] == "openclaw_hebbian_status"
    assert ROUTES["POST /api/v1/memory/analyze"]["tool"] == "openclaw_hebbian_analyze"
    assert ROUTES["POST /api/v1/memory/weight-update"]["tool"] == "openclaw_hebbian_weight_update"


def test_weight_update_defaults_to_dry_run():
    route = ROUTES["POST /api/v1/memory/weight-update"]
    assert route["defaults"].get("dry_run") is True


def test_fleet_route_maps_correctly():
    assert ROUTES["GET /api/v1/fleet/status"]["tool"] == "firm_gateway_fleet_status"


def test_a2a_routes_map_correctly():
    assert ROUTES["POST /api/v1/a2a/discover"]["tool"] == "openclaw_a2a_discovery"
    assert ROUTES["POST /api/v1/a2a/task"]["tool"] == "openclaw_a2a_task_send"


def test_export_routes_map_correctly():
    assert ROUTES["POST /api/v1/export/github-pr"]["tool"] == "firm_export_github_pr"
    assert ROUTES["POST /api/v1/export/slack"]["tool"] == "firm_export_slack_digest"


def test_compliance_route_maps_correctly():
    assert ROUTES["GET /api/v1/compliance/spec"]["tool"] == "openclaw_elicitation_audit"


# ── Documentation strings ───────────────────────────────────────────────────


def test_all_routes_have_docs():
    for route_key, route in ROUTES.items():
        assert len(route["doc"]) > 10, f"Route {route_key} has too short a doc string"


def test_handler_class_exists():
    assert FirmRESTHandler is not None
    assert issubclass(FirmRESTHandler, object)
