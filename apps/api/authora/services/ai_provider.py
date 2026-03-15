"""AI provider abstraction - modular, provider-agnostic."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator

from authora.config import get_settings


@dataclass
class AIResponse:
    """AI completion response with metadata."""

    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str | None = None


class AIProvider(ABC):
    """Abstract AI provider interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        ...

    @abstractmethod
    async def complete_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        """Stream completion. Yields text chunks."""
        ...

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AIResponse:
        """Non-streaming completion with token counts."""
        ...


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    @property
    def name(self) -> str:
        return "openai"

    async def complete_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model = kwargs.get("model") or settings.ai_model or "gpt-4o-mini"
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AIResponse:
        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model = kwargs.get("model") or settings.ai_model or "gpt-4o-mini"
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0] if resp.choices else None
        usage = resp.usage
        return AIResponse(
            text=choice.message.content if choice and choice.message else "",
            provider=self.name,
            model=model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason if choice else None,
        )


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        sys = system_prompt or "You are a helpful writing assistant."
        model = kwargs.get("model") or settings.ai_model or "claude-3-haiku-20240307"

        async with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=sys,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AIResponse:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        sys = system_prompt or "You are a helpful writing assistant."
        model = kwargs.get("model") or settings.ai_model or "claude-3-haiku-20240307"

        resp = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=sys,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text if resp.content else ""
        usage = getattr(resp, "usage", None)
        return AIResponse(
            text=text,
            provider=self.name,
            model=model,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
            finish_reason=None,
        )


def get_provider() -> AIProvider | None:
    """Get configured AI provider."""
    settings = get_settings()
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIProvider()
    if settings.ai_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider()
    return None


async def complete_with_retry(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    max_retries: int = 3,
) -> AsyncGenerator[str, None]:
    """Stream completion with retry. Falls back to legacy complete if no provider."""
    provider = get_provider()
    if provider:
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                async for chunk in provider.complete_stream(
                    prompt, system_prompt, max_tokens
                ):
                    yield chunk
                return
            except Exception as e:
                last_err = e
                if attempt == max_retries - 1:
                    yield f"[AI error after {max_retries} retries: {e}]"
                    return
        if last_err:
            yield f"[AI error: {last_err}]"
    else:
        from authora.services.ai import complete

        async for chunk in complete(prompt, system_prompt, max_tokens):
            yield chunk
