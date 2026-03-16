"""Ollama AI provider - local/self-hosted LLM."""

import json
from typing import AsyncGenerator

import httpx

from authora.services.ai_provider import AIResponse


class OllamaProvider:
    """Ollama API provider for local models."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def name(self) -> str:
        return "ollama"

    def _build_messages(self, prompt: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def complete_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AsyncGenerator[str, None]:
        """Stream completion via Ollama /api/chat."""
        model = kwargs.get("model") or self.model
        messages = self._build_messages(prompt, system_prompt)
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {"num_predict": max_tokens},
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        msg = data.get("message", {})
                        content = msg.get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AIResponse:
        """Non-streaming completion."""
        result: list[str] = []
        async for chunk in self.complete_stream(prompt, system_prompt, max_tokens, **kwargs):
            result.append(chunk)
        text = "".join(result)
        # Ollama doesn't return token counts; estimate
        est_input = max(1, len(prompt) // 4)
        est_output = max(1, len(text) // 4)
        return AIResponse(
            text=text,
            provider=self.name,
            model=kwargs.get("model") or self.model,
            input_tokens=est_input,
            output_tokens=est_output,
        )

    async def list_models(self) -> list[dict]:
        """List available Ollama models via GET /api/tags."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return data.get("models", [])

    async def health_check(self) -> tuple[bool, str]:
        """Check Ollama connectivity. Returns (ok, message)."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    return True, "Ollama is reachable"
                return False, f"Ollama returned {resp.status_code}"
        except httpx.ConnectError as e:
            return False, f"Cannot connect to Ollama: {e}"
        except Exception as e:
            return False, str(e)
