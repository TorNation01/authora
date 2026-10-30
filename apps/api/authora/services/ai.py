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
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
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


async def _openai_once(
    prompt: str,
    system_prompt: str | None,
    max_tokens: int,
    model: str,
) -> str:
    """Single non-streaming call. Returns "" rather than raising on odd payloads."""
    from openai import AsyncOpenAI

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = await client.chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens, stream=False
    )
    message = response.choices[0].message if response.choices else None
    if message is None:
        return ""
    content = (message.content or "").strip()
    if content:
        return content
    # Reasoning-style providers sometimes leave content empty. Only accept the
    # reasoning channel when it reads as finished prose, never as working notes.
    reasoning = (getattr(message, "reasoning_content", "") or "").strip()
    if reasoning and not _looks_like_reasoning(reasoning):
        return reasoning
    return ""


_REASONING_STARTS = (
    "we need", "we must", "the user", "user wants", "okay", "ok,", "let me", "i need",
    "first,", "first ", "so,", "hmm", "let's", "we should", "the task", "task:",
)


def _looks_like_reasoning(text: str) -> bool:
    """True when text is a model's working notes rather than the finished answer."""
    head = text.strip().lower()[:80]
    if any(head.startswith(marker) for marker in _REASONING_STARTS):
        return True
    numbered = head[:3].rstrip(".)").isdigit() and "word" in head
    return numbered


async def complete_sync(prompt: str, system_prompt: str | None = None, max_tokens: int = 2048) -> str:
    """Non-streaming completion. Retries on empty output, then tries the fallback model.

    A model that returns an empty string looks identical to a broken feature to the
    user, so an empty result is treated as a failure worth retrying.
    """
    settings = get_settings()

    result = []
    async for chunk in complete(prompt, system_prompt, max_tokens):
        result.append(chunk)
    text = "".join(result).strip()
    if text:
        return text

    primary = settings.ai_model or "gpt-4o-mini"
    # Reasoning-heavy models can spend the whole budget thinking and return an
    # empty answer; a larger ceiling is what actually fixes that.
    retry_tokens = max(900, max_tokens * 3)
    for _ in range(3):
        try:
            text = await _openai_once(prompt, system_prompt, retry_tokens, primary)
        except Exception:
            text = ""
        if text:
            return text

    fallback = getattr(settings, "ai_fallback_model", None)
    if fallback and fallback != primary:
        try:
            return await _openai_once(prompt, system_prompt, retry_tokens, fallback)
        except Exception:
            return ""
    return ""
