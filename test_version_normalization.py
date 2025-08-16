#!/usr/bin/env python3
"""Unit tests for Windows version normalization in Flask routes.

These tests verify that frontend-provided Windows version strings (e.g.,
"10-pro", "11-enterprise") are normalized by the backend routes to the
expected flags (e.g., "win10pro", "win11ent") before validation and YAML
generation.
"""

import json
import yaml
import pytest
from flask import Flask
from unittest.mock import patch


def _build_test_app():
    """Construct a minimal Flask app and register routes with a dummy limiter.

    We patch RollbackManager.__init__ to avoid permission-sensitive setup
    during module import, and we provide a dummy limiter whose decorator is
    a no-op, so tests don't require flask-limiter.
    """
    # Patch rollback manager init before importing routes so the global
    # instance inside routes is created without side effects.
    with patch('rollback_manager.RollbackManager.__init__', return_value=None):
        import routes as routes_mod

    app = Flask(__name__)

    class DummyLimiter:
        def limit(self, _limit_str):
            def decorator(fn):
                return fn
            return decorator

    routes_mod.register_routes(app, DummyLimiter())
    return app


TEST_APP = _build_test_app()


def _post_generate(payload):
    client = TEST_APP.test_client()
    resp = client.post(
        "/api/generate-config",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    return resp


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Windows 11 versions
        ('11', '11'),
        ('11-pro', '11'),
        ('11-enterprise', '11e'),
        ('11-ltsc', '11l'),
        # Windows 10 versions
        ('10', '10'),
        ('10-pro', '10'),
        ('10-enterprise', '10e'),
        ('10-ltsc', '10l'),
        # Legacy versions
        ('8-enterprise', '8e'),
        ('7-ultimate', '7u'),
        # Windows Server versions
        ('2022', '2022'),
        ('2019', '2019'),
    ],
)
def test_generate_config_normalizes_version(raw, expected):
    payload = {
        "name": f"test-{expected}",
        "version": raw,
        "username": "admin",
        "password": "pass12345",
        # Ensure VERSION appears in environment by providing ram_size
        "ram_size": 4,
        "cpu_cores": 2,
        "disk_size": 40,
    }

    resp = _post_generate(payload)
    assert resp.status_code == 200, resp.get_data(as_text=True)

    data = resp.get_json()
    assert data.get("success") is True
    assert data.get("validation", {}).get("valid") is True

    # Parse docker-compose YAML and verify VERSION env var is normalized
    compose = yaml.safe_load(data["docker_compose"])  # type: ignore[index]
    service_env = compose["services"][payload["name"]]["environment"]
    assert service_env.get('VERSION') == expected, f"Expected VERSION={expected}, got {service_env.get('VERSION')}"

def test_generate_config_uses_windows_version_when_version_missing():
    # No 'version' provided; only 'windows_version' should be normalized and applied
    raw = "10-pro"
    expected = "10"
    name = "test-winver-10pro"

    payload = {
        "name": name,
        "username": "admin",
        "password": "pass12345",
        "windows_version": raw,
        "ram_size": 4,
        "cpu_cores": 2,
        "disk_size": 40,
    }

    resp = _post_generate(payload)
    assert resp.status_code == 200, resp.get_data(as_text=True)

    data = resp.get_json()
    assert data.get("success") is True
    assert data.get("validation", {}).get("valid") is True

    compose = yaml.safe_load(data["docker_compose"])  # type: ignore[index]
    service_env = compose["services"][name]["environment"]
    assert service_env.get("VERSION") == expected
