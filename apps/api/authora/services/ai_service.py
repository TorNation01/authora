"""Unified AI service layer - orchestration, provider, logging, revisions.

All AI flows should go through this service for:
- Provider abstraction (OpenAI, Anthropic, future providers)
- Prompt building
- Usage logging (AIActionLog)
- Revision history (AIRevision on accept)
"""

import uuid
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings


@dataclass
class AICompletionResult:
    """Result of an AI completion with metadata."""

    text: str
    provider: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


async def complete_stream(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    task: str = "general",
    project_prefs: dict | None = None,
    db_overrides: dict[str, str] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream AI completion. Uses provider registry and fallback. Yields text chunks."""
    from authora.services.ai_provider import complete_with_retry

    async for chunk in complete_with_retry(
        prompt,
        system_prompt,
        max_tokens,
        task=task,
        project_prefs=project_prefs,
        db_overrides=db_overrides,
    ):
        yield chunk


async def complete_sync(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    task: str = "general",
    project_prefs: dict | None = None,
    db_overrides: dict[str, str] | None = None,
) -> AICompletionResult:
    """Non-streaming completion with token metadata. Uses provider registry and fallback."""
    from authora.services.ai_registry import get_fallback_chain, get_provider_for_task

    provider, model, provider_name = get_provider_for_task(
        task=task,
        project_prefs=project_prefs,
        db_overrides=db_overrides,
    )
    fallbacks = get_fallback_chain(task, provider_name, db_overrides=db_overrides) if provider else []
    chain = [(provider, model, provider_name)] + fallbacks

    last_err: Exception | None = None
    for p, m, pname in chain:
        if not p:
            continue
        try:
            resp = await p.complete(prompt, system_prompt, max_tokens, model=m)
            return AICompletionResult(
                text=resp.text,
                provider=resp.provider,
                model=resp.model,
                input_tokens=resp.input_tokens,
                output_tokens=resp.output_tokens,
            )
        except Exception as e:
            last_err = e
            continue

    from authora.services.ai import complete

    result = []
    async for chunk in complete(prompt, system_prompt, max_tokens):
        result.append(chunk)
    return AICompletionResult(
        text="".join(result) if result else f"[AI error: {last_err}]"
    )


async def log_ai_action(
    db: AsyncSession,
    user_id: uuid.UUID,
    action_id: str,
    mode: str,
    project_id: uuid.UUID | None = None,
    book_id: uuid.UUID | None = None,
    chapter_id: uuid.UUID | None = None,
    provider: str | None = None,
    model: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    status: str = "completed",
) -> uuid.UUID:
    """Log an AI action for usage accounting and audit."""
    from authora.models import AIActionLog

    log = AIActionLog(
        user_id=user_id,
        project_id=project_id,
        book_id=book_id,
        chapter_id=chapter_id,
        action_id=action_id,
        mode=mode,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        status=status,
    )
    db.add(log)
    await db.flush()
    return log.id


async def create_revision(
    db: AsyncSession,
    user_id: uuid.UUID,
    chapter_id: uuid.UUID,
    action_id: str,
    original_text: str | None,
    suggested_text: str,
    status: str = "pending",
    project_id: uuid.UUID | None = None,
    book_id: uuid.UUID | None = None,
    provider: str | None = None,
    model: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> uuid.UUID:
    """Create an AI revision (pending, accepted, or rejected)."""
    from authora.models import AIRevision

    rev = AIRevision(
        user_id=user_id,
        chapter_id=chapter_id,
        project_id=project_id,
        book_id=book_id,
        action_id=action_id,
        original_text=original_text,
        suggested_text=suggested_text,
        status=status,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    db.add(rev)
    await db.flush()
    return rev.id


def is_ai_configured() -> bool:
    """Check if AI is configured (OpenAI, Anthropic, or Ollama)."""
    s = get_settings()
    return bool(s.openai_api_key or s.anthropic_api_key or s.ollama_enabled)
