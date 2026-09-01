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
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        """Stream completion. Yields text chunks."""
        ...

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
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
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        settings = get_settings()
        base_url = settings.openai_base_url or None
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=base_url)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model = kwargs.get("model") or settings.ai_model or "gpt-4o-mini"
        effective_max_tokens = max_tokens or settings.ai_max_tokens
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=effective_max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AIResponse:
        from openai import AsyncOpenAI

        settings = get_settings()
        base_url = settings.openai_base_url or None
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=base_url)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model = kwargs.get("model") or settings.ai_model or "gpt-4o-mini"
        effective_max_tokens = max_tokens or settings.ai_max_tokens
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=effective_max_tokens,
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
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        sys = system_prompt or "You are a helpful writing assistant."
        model = kwargs.get("model") or settings.ai_model or "claude-3-haiku-20240307"
        effective_max_tokens = max_tokens or settings.ai_max_tokens

        async with client.messages.stream(
            model=model,
            max_tokens=effective_max_tokens,
            system=sys,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AIResponse:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        sys = system_prompt or "You are a helpful writing assistant."
        model = kwargs.get("model") or settings.ai_model or "claude-3-haiku-20240307"
        effective_max_tokens = max_tokens or settings.ai_max_tokens

        resp = await client.messages.create(
            model=model,
            max_tokens=effective_max_tokens,
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


def get_provider(provider_name: str | None = None) -> AIProvider | None:
    """Get configured AI provider. If provider_name given, return that if available."""
    settings = get_settings()
    if provider_name == "openai" and settings.openai_api_key:
        return OpenAIProvider()
    if provider_name == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider()
    if provider_name == "ollama" and settings.ollama_enabled:
        from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model_default,
        )
    if provider_name:
        return None
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIProvider()
    if settings.ai_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider()
    if settings.ai_provider == "ollama" and settings.ollama_enabled:
        from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model_default,
        )
    return None


async def complete_with_retry(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
    task: str = "general",
    project_prefs: dict | None = None,
    user_prefs: dict | None = None,
    preferred_provider: str | None = None,
    preferred_model: str | None = None,
    db_overrides: dict[str, str] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream completion with retry and fallback chain. Respects privacy mode (no cloud fallback)."""
    from authora.services.ai_registry import get_fallback_chain, get_provider_for_task

    provider, model, provider_name = get_provider_for_task(
        task=task,
        project_prefs=project_prefs,
        user_prefs=user_prefs,
        preferred_provider=preferred_provider,
        preferred_model=preferred_model,
        db_overrides=db_overrides,
    )
    fallbacks = (
        get_fallback_chain(
            task, provider_name,
            db_overrides=db_overrides,
            project_prefs=project_prefs,
            user_prefs=user_prefs,
        )
        if provider else []
    )
    chain = [(provider, model, provider_name)] + fallbacks

    last_err: Exception | None = None
    for p, m, pname in chain:
        if not p:
            continue
        for attempt in range(max_retries):
            try:
                async for chunk in p.complete_stream(
                    prompt, system_prompt, max_tokens, model=m
                ):
                    yield chunk
                return
            except Exception as e:
                last_err = e
                if attempt == max_retries - 1:
                    break

    if last_err:
        yield f"[AI error: {last_err}]"
    else:
        from authora.services.ai import complete
        async for chunk in complete(prompt, system_prompt, max_tokens):
            yield chunk
