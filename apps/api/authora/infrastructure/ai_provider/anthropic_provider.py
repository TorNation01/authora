"""Anthropic AI provider."""

from typing import AsyncGenerator

from authora.infrastructure.ai_provider.base import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        client = AsyncAnthropic(api_key=self.api_key)
        sys = system_prompt or "You are a helpful assistant."
        effective_max_tokens = max_tokens or settings.ai_max_tokens

        async with client.messages.stream(
            model=self.model,
            max_tokens=effective_max_tokens,
            system=sys,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def complete_sync(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        result = []
        async for chunk in self.complete(prompt, system_prompt, max_tokens):
            result.append(chunk)
        return "".join(result)
