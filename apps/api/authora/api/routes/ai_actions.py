"""Unified AI actions API - provider-agnostic, mode-aware."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.config import get_settings
from authora.database import get_db
from authora.models import AIRevision, Book, BookSettings, Chapter, Project
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
    mode: str = Field(default="assist", pattern="^(assist|co_write|ghostwriter|editing|spark|idea_generation)$")
    level: str = Field(default="moderate", pattern="^(strict|moderate|creative)$")
    book_type: str = Field(default="general", pattern="^(fiction|nonfiction|general)$")
    extra: dict[str, str] | None = None
    preferred_provider: str | None = None  # openai | anthropic | ollama
    preferred_model: str | None = None


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


@router.post("/actions/run")
async def run_action_stream(
    data: AIActionRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run an AI action and stream the response."""
    from authora.config import get_settings as get_cfg
    from authora.services.billing_service import check_ai_action_limit, has_feature, record_usage

    settings = get_settings()
    has_cloud = bool(settings.openai_api_key or settings.anthropic_api_key)
    has_ollama = settings.ollama_enabled
    if not has_cloud and not has_ollama:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI not configured. Add OpenAI/Anthropic key or enable Ollama.",
        )

    if get_cfg().feature_billing:
        if not await has_feature(db, current_user.id, "ai"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AI features require Premium. Upgrade at /pricing.",
            )
        allowed, used, limit = await check_ai_action_limit(db, current_user.id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"AI action limit reached ({used}/{limit} this month). Upgrade for more.",
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

    book = await get_book_or_404(db, data.book_id, current_user.id)
    project_prefs: dict | None = None
    result = await db.execute(select(BookSettings).where(BookSettings.book_id == data.book_id))
    bs = result.scalar_one_or_none()
    if bs and bs.settings:
        project_prefs = bs.settings.get("ai_prefs") or {}

    from authora.services.ai_registry import action_to_task

    task = action_to_task(data.action_id, data.book_type)

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

    if get_cfg().feature_billing:
        await record_usage(db, current_user.id, "ai_actions", 1)

    from authora.services.ai_service import log_ai_action
    from authora.services.ai_provider import get_provider

    provider = get_provider()
    provider_name = provider.name if provider else None
    model_name = get_settings().ai_model if provider_name else None

    async def generate():
        collected = []
        try:
            async for chunk in complete_with_retry(
                filtered_prompt,
                system_prompt,
                max_tokens=action.max_tokens,
                task=task,
                project_prefs=project_prefs,
                preferred_provider=data.preferred_provider,
                preferred_model=data.preferred_model,
            ):
                collected.append(chunk)
                yield chunk
        finally:
            text = "".join(collected)
            est_output = max(1, len(text) // 4)
            est_input = max(1, len(filtered_prompt) // 4)
            await log_ai_action(
                db,
                current_user.id,
                data.action_id,
                data.mode,
                project_id=None,
                book_id=data.book_id,
                chapter_id=data.chapter_id,
                provider=provider_name,
                model=model_name,
                input_tokens=est_input,
                output_tokens=est_output,
            )

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- Revision history and accept/reject ---

class RevisionCreateRequest(BaseModel):
    """Create a revision for accept/reject tracking."""

    chapter_id: uuid.UUID
    action_id: str
    original_text: str | None = None
    suggested_text: str
    status: str = Field(..., pattern="^(accepted|rejected)$")
    project_id: uuid.UUID | None = None
    book_id: uuid.UUID | None = None


@router.post("/revisions")
async def create_revision(
    data: RevisionCreateRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record a revision (accept or reject) for history."""
    from authora.services.ai_service import create_revision

    if data.book_id:
        await get_book_or_404(db, data.book_id, current_user.id)
    rev_id = await create_revision(
        db,
        current_user.id,
        data.chapter_id,
        data.action_id,
        data.original_text,
        data.suggested_text,
        status=data.status,
        project_id=data.project_id,
        book_id=data.book_id,
    )
    return {"id": str(rev_id), "status": data.status}


@router.get("/revisions")
async def list_revisions(
    chapter_id: uuid.UUID | None = None,
    book_id: uuid.UUID | None = None,
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """List AI revisions for a chapter or book."""
    from sqlalchemy import select

    if not chapter_id and not book_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="chapter_id or book_id required")
    q = select(AIRevision).where(AIRevision.user_id == current_user.id)
    if chapter_id:
        q = q.where(AIRevision.chapter_id == chapter_id)
    if book_id:
        q = q.join(Chapter, AIRevision.chapter_id == Chapter.id).where(Chapter.book_id == book_id)
    q = q.order_by(AIRevision.created_at.desc()).limit(50)
    result = await db.execute(q)
    revs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "chapter_id": str(r.chapter_id),
            "action_id": r.action_id,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in revs
    ]
