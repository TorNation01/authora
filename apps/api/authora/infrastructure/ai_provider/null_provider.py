"""Null AI provider - no-op when AI not configured."""

from typing import AsyncGenerator

from authora.infrastructure.ai_provider.base import AIProvider


class NullAIProvider(AIProvider):
    """No-op provider when AI is not configured."""

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        yield "[AI not configured. Add OpenAI or Anthropic API key in settings.]"

    async def complete_sync(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
    ) -> str:
        return "[AI not configured. Add OpenAI or Anthropic API key in settings.]"
