"""AI service - OpenAI and Anthropic integration."""

from typing import AsyncGenerator

from authora.config import get_settings


async def complete(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    """Stream AI completion. Yields chunks."""
    settings = get_settings()
    provider = settings.ai_provider

    if provider == "openai" and settings.openai_api_key:
        async for chunk in _openai_complete(prompt, system_prompt, max_tokens):
            yield chunk
    elif provider == "anthropic" and settings.anthropic_api_key:
        async for chunk in _anthropic_complete(prompt, system_prompt, max_tokens):
            yield chunk
    else:
        yield "[AI not configured. Add OpenAI or Anthropic API key in settings.]"


async def _openai_complete(
    prompt: str,
    system_prompt: str | None,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """OpenAI completion."""
    from openai import AsyncOpenAI

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    stream = await client.chat.completions.create(
        model=settings.ai_model or "gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def _anthropic_complete(
    prompt: str,
    system_prompt: str | None,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """Anthropic completion."""
    from anthropic import AsyncAnthropic

    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    sys = system_prompt or "You are a helpful writing assistant."
    model = settings.ai_model or "claude-3-haiku-20240307"

    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=sys,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def complete_sync(prompt: str, system_prompt: str | None = None, max_tokens: int = 2048) -> str:
    """Non-streaming completion. Returns full text."""
    result = []
    async for chunk in complete(prompt, system_prompt, max_tokens):
        result.append(chunk)
    return "".join(result)
