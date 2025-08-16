#!/usr/bin/env python3
"""Unit tests for rollback info integration with version normalization.

These tests use Flask's test_client and patch RollbackManager to avoid
platform-specific and privileged operations, while verifying that:
- UI-provided Windows version strings are normalized server-side.
- When enable_rollback is True on a non-Linux stub, the route injects
  mock rollback info with expected fields.
"""

import json
import yaml
import pytest
from flask import Flask
from unittest.mock import patch
import importlib, sys


def _build_test_app_with_mock_rb():
    """Construct a Flask app with routes registered and a mocked RollbackManager.

    We patch RollbackManager.__init__ to set minimal attributes used by routes
    and avoid any side effects. We then register routes with a dummy limiter.
    """

    # Define a stub RollbackManager class to avoid side effects
    class StubRollbackManager:
        def __init__(self):
            # Force non-Linux path so the route produces mock rollback info
            self.is_linux = False
            self.revertit_available = False
            self.active_checkpoints = {}
            self.timeout_defaults = {"container": 180, "macvlan": 420}

        # Provide minimal method stubs if ever invoked
        def create_checkpoint(self, *args, **kwargs):
            return {"success": False, "checkpoint_id": None}

        def start_monitoring(self, *args, **kwargs):
            return {"success": False}

        def confirm_checkpoint(self, *args, **kwargs):
            return {"success": True}

        def trigger_rollback(self, *args, **kwargs):
            return {"success": True}

    with patch('rollback_manager.RollbackManager', new=StubRollbackManager):
        # Ensure we import/reload routes while patched so its globals
        # (like rollback_manager) are initialized with our stub
        if 'routes' in sys.modules:
            routes_mod = importlib.reload(sys.modules['routes'])
        else:
            import routes as routes_mod

    app = Flask(__name__)

    class DummyLimiter:
        def limit(self, _limit_str):
            def decorator(fn):
                return fn
            return decorator

    routes_mod.register_routes(app, DummyLimiter())
    return app


def _post_generate(app, payload):
    client = app.test_client()
    return client.post(
        "/api/generate-config",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


def test_generate_config_adds_mock_rollback_and_normalizes_version():
    app = _build_test_app_with_mock_rb()

    payload = {
        "name": "rb-test-11ent",
        "windows_version": "11-enterprise",  # raw UI value
        "username": "admin",
        "password": "pass12345",
        # Ensure VERSION appears in environment by providing ram_size
        "ram_size": 8,
        "cpu_cores": 2,
        "disk_size": 40,
        # Enable rollback; on our mocked non-Linux manager, this yields mock info
        "enable_rollback": True,
        # minutes -> route converts to seconds
        "rollback_timeout": 7,
    }

    resp = _post_generate(app, payload)
    assert resp.status_code == 200, resp.get_data(as_text=True)

    data = resp.get_json()
    assert data.get("success") is True
    assert data.get("validation", {}).get("valid") is True

    # Verify rollback info is present and mocked
    rb = data.get("rollback")
    assert isinstance(rb, dict)
    assert rb.get("mock") is True
    assert rb.get("enabled") is False
    assert isinstance(rb.get("checkpoint_id"), str)
    assert rb["checkpoint_id"].startswith("test_container_")
    assert rb.get("timeout") == 7 * 60

    # Verify version normalization in docker-compose env vars
    compose = yaml.safe_load(data["docker_compose"])  # type: ignore[index]
    service_env = compose["services"][payload["name"]]["environment"]
    assert service_env.get("VERSION") == "11e"


def test_generate_config_mock_rollback_for_macvlan():
    app = _build_test_app_with_mock_rb()

    payload = {
        "name": "rb-test-macvlan-10pro",
        "version": "10-pro",
        "username": "admin",
        "password": "pass12345",
        "ram_size": 4,
        "cpu_cores": 2,
        "disk_size": 40,
        "enable_rollback": True,
        "rollback_timeout": 3,
        # Force change_type to macvlan
        "network_mode": "macvlan",
        # Minimal required macvlan fields to pass validation
        "macvlan_subnet": "192.168.1.0/24",
        "macvlan_gateway": "192.168.1.1",
        "macvlan_parent": "eth0",
    }

    resp = _post_generate(app, payload)
    assert resp.status_code == 200, resp.get_data(as_text=True)

    data = resp.get_json()
    assert data.get("success") is True
    assert data.get("validation", {}).get("valid") is True

    rb = data.get("rollback")
    assert isinstance(rb, dict)
    assert rb.get("mock") is True
    assert rb.get("enabled") is False
    assert isinstance(rb.get("checkpoint_id"), str)
    assert rb["checkpoint_id"].startswith("test_macvlan_")
    assert rb.get("timeout") == 3 * 60

    # Verify version normalization in docker-compose env vars
    compose = yaml.safe_load(data["docker_compose"])  # type: ignore[index]
    service_env = compose["services"][payload["name"]]["environment"]
    assert service_env.get("VERSION") == "10"
