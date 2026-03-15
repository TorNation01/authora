"""AI provider factory."""

from functools import lru_cache

from authora.config import get_settings
from authora.infrastructure.ai_provider.anthropic_provider import AnthropicProvider
from authora.infrastructure.ai_provider.base import AIProvider
from authora.infrastructure.ai_provider.null_provider import NullAIProvider
from authora.infrastructure.ai_provider.openai_provider import OpenAIProvider


@lru_cache
def get_ai_provider() -> AIProvider:
    """Get configured AI provider."""
    settings = get_settings()
    provider = getattr(settings, "ai_provider", "openai") or "openai"

    if provider == "openai" and settings.openai_api_key:
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=getattr(settings, "ai_model", "gpt-4o-mini") or "gpt-4o-mini",
        )
    if provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=getattr(settings, "ai_model", "claude-3-haiku-20240307") or "claude-3-haiku-20240307",
        )
    return NullAIProvider()
