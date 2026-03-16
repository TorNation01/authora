"""Setup wizard request/response schemas."""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _mask_secret(v: str | None) -> str | None:
    if not v:
        return v
    if len(v) <= 4:
        return "****"
    return v[:2] + "*" * (len(v) - 4) + v[-2:]


class SetupBranding(BaseModel):
    """Branding configuration."""

    product_name: str = Field(..., min_length=1, max_length=100)
    tagline: str = Field(default="AI-Powered Book Builder", max_length=200)


class SetupDomain(BaseModel):
    """Domain and SSL configuration."""

    domain: str = Field(default="localhost", max_length=255)
    use_ssl: bool = Field(default=False, description="Expect HTTPS in production")
    ssl_auto: bool = Field(default=True, description="Use automatic SSL (e.g. Let's Encrypt)")


class SetupDatabase(BaseModel):
    """Database connection."""

    database_url: str = Field(..., min_length=10)


class SetupRedis(BaseModel):
    """Redis connection."""

    redis_url: str = Field(..., min_length=10)


class SetupStorage(BaseModel):
    """Storage configuration."""

    storage_provider: Literal["local", "s3", "r2"] = "local"
    storage_local_path: str = Field(default="./storage", max_length=500)
    s3_bucket: str | None = None
    r2_bucket: str | None = None
    r2_account_id: str | None = None
    aws_region: str = Field(default="us-east-1", max_length=50)


class SetupAI(BaseModel):
    """AI provider keys."""

    ai_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    ai_model: str = Field(default="gpt-4o-mini", max_length=100)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_enabled: bool = False
    ollama_base_url: str = Field(default="http://localhost:11434", max_length=255)


class SetupEmail(BaseModel):
    """Email provider (optional)."""

    enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    from_email: str | None = None


class SetupAdmin(BaseModel):
    """First admin account."""

    admin_email: str = Field(..., min_length=3)
    admin_password: str = Field(..., min_length=8)
    admin_display_name: str = Field(default="Admin", max_length=100)

    @field_validator("admin_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()


class SetupPreferences(BaseModel):
    """Backup, reminders, analytics."""

    backup_enabled: bool = Field(default=True)
    backup_retention_days: int = Field(default=7, ge=1, le=90)
    reminder_enabled: bool = Field(default=True)
    reminder_default_time: str = Field(default="09:00", pattern=r"^\d{2}:\d{2}$")
    analytics_enabled: bool = Field(default=False)
    telemetry_enabled: bool = Field(default=False)


class SetupMode(BaseModel):
    """Local vs cloud mode."""

    mode: Literal["local", "cloud"] = "local"


class SetupTestRequest(BaseModel):
    """Request to test a connection."""

    database_url: str | None = None
    redis_url: str | None = None
    ollama_base_url: str | None = None


class SetupApplyRequest(BaseModel):
    """Full config to apply (write to .env)."""

    branding: SetupBranding | None = None
    domain: SetupDomain | None = None
    database_url: str | None = None
    redis_url: str | None = None
    storage: SetupStorage | None = None
    ai: SetupAI | None = None
    email: SetupEmail | None = None
    admin: SetupAdmin | None = None
    preferences: SetupPreferences | None = None
    mode: SetupMode | None = None
    secret_key: str | None = None


class SetupFinalizeRequest(BaseModel):
    """Finalize setup - run migrations, seed, create admin."""

    database_url: str
    admin: SetupAdmin
    ai: SetupAI | None = None
    run_migrations: bool = True
    seed_templates: bool = True


class SetupValidationResult(BaseModel):
    """Validation result for a field."""

    valid: bool
    message: str | None = None


class SetupTestResult(BaseModel):
    """Connection test result."""

    database: SetupValidationResult | None = None
    redis: SetupValidationResult | None = None
    ollama: SetupValidationResult | None = None
