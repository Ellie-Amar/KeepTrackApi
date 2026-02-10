from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KeepTrack"
    app_version: str = "0.1.0"

    database_url: str | None = None

    jwt_secret: str = "uwu-secret"
    jwt_issuer: str = "keeptrack"
    jwt_access_ttl_minutes: int = 60
    jwt_refresh_ttl_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
