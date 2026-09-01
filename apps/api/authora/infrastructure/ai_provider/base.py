"""AI provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class AIProvider(ABC):
    """Abstract AI/LLM provider."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream completion. Yields text chunks."""
        ...

    @abstractmethod
    async def complete_sync(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Non-streaming completion. Returns full text."""
        ...
