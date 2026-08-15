from functools import lru_cache
import os
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("APP_ENVIRONMENT") == "development" else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )
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
    s3_region: str = "us-east-1"
    media_storage_provider: Literal["local", "minio", "s3"] = "local"
    media_storage_path: Path = Path("/tmp/dating-platform-media")
    media_upload_chunk_bytes: int = Field(default=1024 * 1024, ge=64 * 1024, le=16 * 1024 * 1024)
    media_image_max_upload_bytes: int = Field(default=25 * 1024 * 1024, ge=1)
    media_video_max_upload_bytes: int = Field(default=100 * 1024 * 1024, ge=1)
    media_storage_timeout_seconds: int = Field(default=30, ge=1, le=300)
    media_storage_retry_attempts: int = Field(default=3, ge=1, le=10)
    media_signed_url_expiry_seconds: int = Field(default=900, ge=60, le=86400)
    media_image_large_px: int = Field(default=2048, ge=320, le=8192)
    media_image_medium_px: int = Field(default=1280, ge=320, le=8192)
    media_image_small_px: int = Field(default=640, ge=160, le=8192)
    media_thumbnail_px: int = Field(default=320, ge=64, le=2048)
    media_image_jpeg_quality: int = Field(default=85, ge=50, le=95)
    media_image_webp_quality: int = Field(default=82, ge=50, le=95)
    media_video_display_px: int = Field(default=1280, ge=320, le=4096)
    media_video_thumbnail_px: int = Field(default=640, ge=160, le=2048)
    media_video_thumbnail_second: int = Field(default=1, ge=0, le=60)
    media_processing_stale_seconds: int = Field(default=3600, ge=60, le=604800)
    presence_away_seconds: int = Field(default=300, ge=10, le=3600)
    presence_offline_seconds: int = Field(default=900, ge=30, le=86400)
    typing_ttl_seconds: int = Field(default=8, ge=2, le=60)

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        self.database_url = self._railway_database_url(self.database_url)
        if self.app_environment == "production" and self.app_debug:
            raise ValueError("APP_DEBUG must be false in production")
        if self.jwt_secret_key.get_secret_value().startswith("replace-"):
            raise ValueError("JWT_SECRET_KEY must be replaced")
        return self

    @staticmethod
    def _railway_database_url(database_url: PostgresDsn) -> PostgresDsn:
        pg_host = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST")
        pg_port = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT")
        pg_db = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")
        pg_user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")
        pg_password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")

        if not all([pg_host, pg_port, pg_db, pg_user, pg_password]):
            return database_url

        railway_url = (
            f"postgresql://{quote_plus(pg_user)}:{quote_plus(pg_password)}"
            f"@{pg_host}:{pg_port}/{pg_db}"
        )
        return PostgresDsn(railway_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
