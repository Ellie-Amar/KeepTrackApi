from __future__ import annotations
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    app_name: str = "KeepTrack"
    app_version: str = "0.1.0"
    app_env: str = "dev"

    database_url: str | None = None

    jwt_secret: str | None = None
    jwt_issuer: str = "keeptrack"
    jwt_access_ttl_minutes: int = 60
    jwt_refresh_ttl_minutes: int = 60 * 24 * 7

    @model_validator(mode="after")
    def _validate_security_settings(self) -> Settings:
        env = self.app_env.lower()
        if self.jwt_secret:
            return self
        if env in {"dev", "test"}:
            # Dev/test fallback to keep local runs simple while making risk explicit.
            self.jwt_secret = "dev-insecure-jwt-secret"
            warnings.warn(
                "JWT_SECRET is not set; using insecure dev/test fallback secret.",
                RuntimeWarning,
                stacklevel=2,
            )
            return self
        raise ValueError("JWT_SECRET must be set when APP_ENV is production")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
