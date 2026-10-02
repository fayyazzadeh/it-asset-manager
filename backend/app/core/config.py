from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IT Asset Manager"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://it_asset_manager:change-me@localhost:5432/it_asset_manager"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-this-in-development"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()