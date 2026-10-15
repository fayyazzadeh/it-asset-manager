from fastapi.testclient import TestClient

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
