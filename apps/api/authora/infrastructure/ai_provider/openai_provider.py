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
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete_sync(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
    ) -> str:
        result = []
        async for chunk in self.complete(prompt, system_prompt, max_tokens):
            result.append(chunk)
        return "".join(result)
