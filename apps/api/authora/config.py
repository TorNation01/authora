"""Application configuration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "AUTHORA"
    debug: bool = False

    # Deployment mode: standalone | anakatech
    deployment_mode: str = "standalone"

    # Feature flags (environment-driven)
    feature_standalone_auth: bool = True
    feature_standalone_landing: bool = True
    feature_standalone_setup_wizard: bool = True
    feature_local_admin_creation: bool = True
    feature_sso_ready: bool = False
    feature_embeddable_shell: bool = False
    feature_shared_notifications: bool = False
    feature_shared_workspace_identity: bool = False
    feature_tenant_aware: bool = False
    feature_billing: bool = False

    # White-label branding (overridable via env)
    branding_product_name: str = "AUTHORA"
    branding_tagline: str = "AI-Powered Book Builder"
    branding_logo_url: Optional[str] = None
    branding_favicon_url: Optional[str] = None
    branding_primary_color: Optional[str] = None
    branding_show_powered_by: bool = True

    # Database
    database_url: str = "postgresql://authora:authora@localhost:5432/authora"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    sso_issuer_url: Optional[str] = None
    sso_client_id: Optional[str] = None
    sso_metadata_url: Optional[str] = None

    # AI (optional - configured via setup wizard)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_provider: str = "openai"  # openai | anthropic
    ai_model: str = "gpt-4o-mini"
    ai_rate_limit_per_minute: Optional[int] = 60

    # Export
    max_export_size_mb: int = 50

    # Notifications (email)
    notification_email_provider: str = "none"  # none | smtp | sendgrid
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    from_email: Optional[str] = None  # Alias used by setup wizard; fallback for smtp_from_email
    sendgrid_api_key: Optional[str] = None

    @property
    def email_from(self) -> str:
        """From address for emails; setup wizard may set FROM_EMAIL."""
        return self.smtp_from_email or self.from_email or self.smtp_user or "noreply@authora.app"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Storage
    storage_provider: str = "local"
    storage_local_path: str = "./storage"
    s3_bucket: str | None = None
    r2_bucket: str | None = None
    r2_account_id: str | None = None
    aws_region: str = "us-east-1"

    # API gateway (for Anakatech: upstream gateway URL)
    api_gateway_url: Optional[str] = None

    # Cron / internal jobs (secret header for /accountability/cron/reminders)
    cron_secret: Optional[str] = None

    @field_validator("deployment_mode", mode="before")
    @classmethod
    def validate_deployment_mode(cls, v: str) -> str:
        allowed = ("standalone", "anakatech")
        if v and v.lower() in allowed:
            return v.lower()
        return "standalone"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Warn or fail on insecure config in production."""
        if os.getenv("AUTHORA_SKIP_SECRET_VALIDATION") == "1":
            return self
        default_secret = "change-me-in-production-use-openssl-rand-hex-32"
        if self.secret_key == default_secret and not self.debug:
            import warnings
            warnings.warn(
                "SECRET_KEY is default. Set a strong secret in production: openssl rand -hex 32",
                UserWarning,
                stacklevel=2,
            )
        return self

    def is_standalone(self) -> bool:
        return self.deployment_mode == "standalone"

    def is_anakatech(self) -> bool:
        return self.deployment_mode == "anakatech"

    def get_feature_flags(self) -> dict[str, bool]:
        """Return feature flags for API consumers."""
        return {
            "standalone_auth": self.feature_standalone_auth,
            "standalone_landing": self.feature_standalone_landing,
            "standalone_setup_wizard": self.feature_standalone_setup_wizard,
            "local_admin_creation": self.feature_local_admin_creation,
            "sso_ready": self.feature_sso_ready,
            "embeddable_shell": self.feature_embeddable_shell,
            "shared_notifications": self.feature_shared_notifications,
            "shared_workspace_identity": self.feature_shared_workspace_identity,
            "tenant_aware": self.feature_tenant_aware,
            "billing": self.feature_billing,
        }

    def get_branding(self) -> dict:
        """Return branding config for white-label."""
        return {
            "product_name": self.branding_product_name,
            "tagline": self.branding_tagline,
            "logo_url": self.branding_logo_url,
            "favicon_url": self.branding_favicon_url,
            "primary_color": self.branding_primary_color,
            "show_powered_by": self.branding_show_powered_by,
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
