import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="change-this-in-development",
            database_url="postgresql+psycopg://itam:strong-db-password@localhost:5432/itam",
        )


def test_production_rejects_short_jwt_secret():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="too-short",
            database_url="postgresql+psycopg://itam:strong-db-password@localhost:5432/itam",
        )


def test_production_rejects_default_database_password():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="a-long-random-production-secret-that-is-not-a-default",
            database_url="postgresql+psycopg://itam:change-me@localhost:5432/itam",
        )


def test_development_can_use_local_defaults():
    settings = Settings(environment="development")
    assert settings.environment == "development"
