from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "dating-platform-api"
    app_environment: Literal["development", "test", "staging", "production"] = "development"
    app_debug: bool = False
    app_log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    database_url: PostgresDsn
    redis_url: RedisDsn
    backend_cors_origins: list[AnyHttpUrl] = Field(default_factory=list)
    trusted_hosts: list[str] = Field(default_factory=lambda: ["localhost"])
    jwt_secret_key: SecretStr
    access_token_minutes: int = Field(default=15, ge=5, le=60)
    refresh_token_days: int = Field(default=30, ge=1, le=90)
    email_token_hours: int = Field(default=24, ge=1, le=168)
    password_reset_minutes: int = Field(default=30, ge=5, le=120)
    cookie_secure: bool = False
    auth_rate_limit_per_minute: int = Field(default=10, ge=1, le=100)
    s3_endpoint_url: str
    s3_bucket: str
    s3_access_key_id: str
    s3_secret_access_key: SecretStr
    media_storage_path: Path = Path("/tmp/dating-platform-media")

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.app_environment == "production" and self.app_debug:
            raise ValueError("APP_DEBUG must be false in production")
        if self.jwt_secret_key.get_secret_value().startswith("replace-"):
            raise ValueError("JWT_SECRET_KEY must be replaced")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
