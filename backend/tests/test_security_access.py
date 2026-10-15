from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core import permissions
from app.core.permissions import AuthenticatedPrincipal, require_roles
from app.core.config import settings
from app.db import get_db
from app.main import app


class EmptySession:
    def scalars(self, *_args, **_kwargs):
        return []

    def scalar(self, *_args, **_kwargs):
        return None

    def get(self, *_args, **_kwargs):
        return None


def override_db():
    yield EmptySession()


def test_asset_routes_require_authentication():
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).get("/api/assets")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_discovery_preview_requires_authentication():
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).post("/api/discovery/preview", json={"fields": {"HOSTNAME": "pc01"}})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_health_remains_public():
    response = TestClient(app).get("/health")
    assert response.status_code == 200


def test_role_guard_allows_explicitly_permitted_role():
    principal = AuthenticatedPrincipal(user_id=7, username="operator", roles=frozenset({"OPERATOR"}))
    guard = require_roles("ADMIN", "OPERATOR")

    assert guard(principal) == principal


def test_role_guard_rejects_unpermitted_role():
    principal = AuthenticatedPrincipal(user_id=8, username="viewer", roles=frozenset({"VIEWER"}))
    guard = require_roles("ADMIN", "OPERATOR")

    try:
        guard(principal)
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("role guard should reject VIEWER for a write operation")


def test_registration_is_disabled_without_bootstrap_flag(monkeypatch):
    monkeypatch.setattr(settings, "bootstrap_admin_enabled", False)
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).post(
            "/api/auth/register",
            json={"username": "first-admin", "email": "admin@example.com", "password": "long-enough-test-password"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
