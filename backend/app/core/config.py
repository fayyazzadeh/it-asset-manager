from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    app_name: str = "IT Asset Manager"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://it_asset_manager:change-me@localhost:5432/it_asset_manager"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-this-in-development"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    bootstrap_admin_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.strip().lower() not in {"production", "prod"}:
            return self

        if len(self.jwt_secret) < 32 or self.jwt_secret.strip().lower() in {
            "change-this-in-development",
            "secret",
            "changeme",
        }:
            raise ValueError("Production requires a non-default JWT_SECRET of at least 32 characters")

        try:
            database_password = make_url(self.database_url).password
        except Exception as exc:
            raise ValueError("Production DATABASE_URL must be a valid SQLAlchemy URL") from exc

        if not database_password or database_password.strip().lower() in {
            "change-me",
            "changeme",
            "password",
            "postgres",
        }:
            raise ValueError("Production DATABASE_URL must contain a non-default database password")

        return self


settings = Settings()
