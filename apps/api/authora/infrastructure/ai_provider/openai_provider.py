"""OpenAI AI provider."""

from typing import AsyncGenerator

from authora.infrastructure.ai_provider.base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        settings = get_settings()
        base_url = settings.openai_base_url or None
        client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        effective_max_tokens = max_tokens or settings.ai_max_tokens
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=effective_max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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
