"""Unified AI actions API - provider-agnostic, mode-aware."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.models import Book, Project
from authora.services.ai_orchestration import (
    ACTION_DEFINITIONS,
    AIMode,
    AssistanceLevel,
    BookType,
    build_user_prompt,
    build_system_prompt,
    build_workspace_context,
    get_action_definition,
)
from authora.services.ai_provider import complete_with_retry
from authora.services.ai_safety import check_rate_limit, filter_prompt

router = APIRouter(prefix="/ai", tags=["ai-actions"])


class AIActionRequest(BaseModel):
    """Request for an AI action."""

    action_id: str = Field(..., description="Action type (e.g. rewrite_sentence)")
    book_id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    selection: str | None = None
    context: str | None = None
    mode: str = Field(default="assist", pattern="^(assist|co_write|ghostwriter|editing|idea_generation)$")
    level: str = Field(default="moderate", pattern="^(strict|moderate|creative)$")
    book_type: str = Field(default="general", pattern="^(fiction|nonfiction|general)$")
    extra: dict[str, str] | None = None


class AIActionResponse(BaseModel):
    """Response metadata (for non-streaming)."""

    action_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    provider: str = ""


@router.get("/actions", response_model=list[dict])
async def list_actions():
    """List available AI actions."""
    return [
        {
            "id": a.id,
            "label": a.label,
            "description": a.description,
            "uses_selection": a.uses_selection,
            "uses_context": a.uses_context,
        }
        for a in ACTION_DEFINITIONS.values()
    ]


async def get_book_or_404(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book:
    result = await db.execute(
        select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("/actions/run")
async def run_action_stream(
    data: AIActionRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run an AI action and stream the response."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI not configured",
        )

    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in a minute.",
        )

    action = get_action_definition(data.action_id)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action: {data.action_id}",
        )

    selection = data.selection or ""
    context = data.context or ""

    if action.uses_selection and not selection and not context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This action requires a selection or context",
        )

    user_prompt = build_user_prompt(
        data.action_id,
        BookType(data.book_type),
        selection=selection,
        context=context,
        extra=data.extra,
    )

    filtered_prompt, is_safe = filter_prompt(user_prompt)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt was filtered for safety",
        )

    await get_book_or_404(db, data.book_id, current_user.id)

    workspace_context = await build_workspace_context(
            db,
            data.book_id,
            BookType(data.book_type),
            chapter_id=data.chapter_id,
            include_recent=bool(data.chapter_id),
        )

    system_prompt = build_system_prompt(
        AIMode(data.mode),
        AssistanceLevel(data.level),
        BookType(data.book_type),
        workspace_context=workspace_context,
    )

    async def generate():
        async for chunk in complete_with_retry(
            filtered_prompt,
            system_prompt,
            max_tokens=action.max_tokens,
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
