"""
AI provider configuration - validation, provider toggles, per-environment support.

Provides:
- Provider-specific config validation
- Per-environment provider toggles (dev/staging/prod)
- Secret-safe logging (never log keys)
- Graceful degraded mode when providers unavailable
"""

import logging
import os
import re
from typing import Any

from authora.config import get_settings

logger = logging.getLogger(__name__)

# Secret patterns - never log these
SECRET_PATTERNS = (
    r"sk-[a-zA-Z0-9]{20,}",
    r"sk-ant-[a-zA-Z0-9\-]{20,}",
    r"AIza[a-zA-Z0-9_-]{35}",
)


def _redact_secrets(text: str) -> str:
    """Redact secret-like substrings from log messages."""
    for pat in SECRET_PATTERNS:
        text = re.sub(pat, "***REDACTED***", text)
    return text


def log_provider_status(provider: str, configured: bool, message: str = "") -> None:
    """Log provider status without exposing secrets."""
    status = "configured" if configured else "not configured"
    safe_msg = _redact_secrets(message) if message else ""
    logger.info("AI provider %s: %s%s", provider, status, f" — {safe_msg}" if safe_msg else "")


def validate_openai_config() -> tuple[bool, str]:
    """Validate OpenAI config. Returns (ok, message)."""
    s = get_settings()
    if not s.openai_api_key:
        return False, "OPENAI_API_KEY not set"
    key = s.openai_api_key
    if not key.startswith("sk-") or len(key) < 20:
        return False, "OPENAI_API_KEY format invalid"
    return True, "OK"


def validate_anthropic_config() -> tuple[bool, str]:
    """Validate Anthropic config. Returns (ok, message)."""
    s = get_settings()
    if not s.anthropic_api_key:
        return False, "ANTHROPIC_API_KEY not set"
    key = s.anthropic_api_key
    if not key.startswith("sk-ant-") or len(key) < 20:
        return False, "ANTHROPIC_API_KEY format invalid"
    return True, "OK"


def validate_ollama_config() -> tuple[bool, str]:
    """Validate Ollama config. Returns (ok, message)."""
    s = get_settings()
    if not s.ollama_enabled:
        return False, "Ollama not enabled"
    url = s.ollama_base_url or ""
    if not url or not url.startswith(("http://", "https://")):
        return False, "OLLAMA_BASE_URL must be http(s) URL"
    return True, "OK"


def validate_gemini_config() -> tuple[bool, str]:
    """Validate Gemini config (slot ready). Returns (ok, message)."""
    s = get_settings()
    key = getattr(s, "gemini_api_key", None)
    if not key:
        return False, "GEMINI_API_KEY not set"
    if not key.startswith("AIza") or len(key) < 30:
        return False, "GEMINI_API_KEY format invalid"
    return True, "OK"


def get_available_providers() -> dict[str, bool]:
    """Return which providers are configured (not necessarily healthy)."""
    s = get_settings()
    cloud_disabled = getattr(s, "ai_cloud_disabled", False)
    local_only = getattr(s, "ai_local_only", False)

    result: dict[str, bool] = {}
    result["openai"] = bool(s.openai_api_key) and not cloud_disabled
    result["anthropic"] = bool(s.anthropic_api_key) and not cloud_disabled
    result["gemini"] = bool(getattr(s, "gemini_api_key", None)) and not cloud_disabled
    result["ollama"] = s.ollama_enabled

    if local_only or cloud_disabled:
        result["openai"] = False
        result["anthropic"] = False
        result["gemini"] = False

    return result


def is_ai_available() -> bool:
    """True if at least one AI provider is configured."""
    return any(get_available_providers().values())


def get_environment() -> str:
    """Resolve environment: development, staging, production."""
    env = os.getenv("AUTHORA_ENV") or os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV", "development")
    env = str(env).lower()
    if env in ("prod", "production"):
        return "production"
    if env in ("staging", "stage"):
        return "staging"
    return "development"
