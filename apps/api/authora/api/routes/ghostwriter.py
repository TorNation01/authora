"""Ghostwriter mode API - intake, outline, briefs, draft generation."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.config import get_settings
from authora.database import get_db
from authora.models import Book, Chapter, ChapterBrief, ChapterVersion, GhostwriterWorkspace, Project
from authora.schemas.ghostwriter import (
    ApplyDraftRequest,
    GhostwriterIntakeCreate,
    GhostwriterOutlineApprove,
    GhostwriterWorkspaceResponse,
    GenerateDraftRequest,
    RegenerateSectionRequest,
    RewriteWithFeedbackRequest,
)
from authora.services.export import plain_text_to_tiptap
from authora.services.ghostwriter_ai import (
    generate_chapter_brief,
    generate_chapter_draft,
    generate_outline,
    regenerate_section,
    rewrite_with_feedback,
)
from authora.services.ai_safety import check_rate_limit

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}/ghostwriter", tags=["ghostwriter"])


async def get_or_create_workspace(db: AsyncSession, book_id: uuid.UUID) -> GhostwriterWorkspace:
    result = await db.execute(
        select(GhostwriterWorkspace).options(selectinload(GhostwriterWorkspace.chapter_briefs)).where(
            GhostwriterWorkspace.book_id == book_id
        )
    )
    ws = result.scalar_one_or_none()
    if not ws:
        ws = GhostwriterWorkspace(book_id=book_id)
        db.add(ws)
        await db.flush()
        await db.refresh(ws)
    return ws


@router.get("", response_model=GhostwriterWorkspaceResponse)
async def get_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get or create ghostwriter workspace."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    return GhostwriterWorkspaceResponse.model_validate(ws)


@router.post("/intake", response_model=GhostwriterWorkspaceResponse)
async def submit_intake(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: GhostwriterIntakeCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit intake questionnaire."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    ws.mode = data.mode
    ws.intake_answers = data.intake_answers
    ws.voice_tone = data.voice_tone
    ws.target_audience = data.target_audience
    ws.desired_outcome = data.desired_outcome
    ws.workflow_step = "outline"
    await db.flush()
    await db.refresh(ws)
    return GhostwriterWorkspaceResponse.model_validate(ws)


async def _check_ghostwriter_access(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Require ghostwriter feature and ghostwriter session limit when billing enabled."""
    if not get_settings().feature_billing:
        return
    from authora.services.billing_service import check_ghostwriter_limit, has_feature, record_usage

    if not await has_feature(db, user_id, "ghostwriter"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ghostwriter requires Premium. Upgrade at /pricing.",
        )
    allowed, used, limit = await check_ghostwriter_limit(db, user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ghostwriter limit reached ({used}/{limit} this month). Upgrade for more.",
        )
    await record_usage(db, user_id, "ghostwriter_sessions", 1)


@router.post("/outline/generate")
async def generate_outline_endpoint(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate book outline from intake."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")
    await _check_ghostwriter_access(db, current_user.id)
    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    outline = await generate_outline(db, book_id, book.type or "general", ws)
    ws.outline = outline
    ws.workflow_step = "outline"
    await db.flush()
    return {"outline": outline}


@router.post("/outline/approve", response_model=GhostwriterWorkspaceResponse)
async def approve_outline(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: GhostwriterOutlineApprove,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Approve outline (with optional edits). Creates chapters from outline."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    ws.outline = data.outline
    ws.outline_approved_at = datetime.now(timezone.utc)
    ws.workflow_step = "briefs"

    # Ensure chapters exist from outline
    chapters_data = data.outline.get("chapters", [])
    result = await db.execute(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order))
    existing = list(result.scalars().all())
    for i, ch_data in enumerate(chapters_data):
        title = ch_data.get("title", f"Chapter {i + 1}")
        if i < len(existing):
            if existing[i].title != title:
                existing[i].title = title
        else:
            ch = Chapter(
                book_id=book_id,
                title=title,
                sort_order=i,
                content={"type": "doc", "content": [{"type": "paragraph"}]},
            )
            db.add(ch)
            await db.flush()
    await db.flush()
    await db.refresh(ws)
    return GhostwriterWorkspaceResponse.model_validate(ws)


@router.post("/briefs/{chapter_id}/generate")
async def generate_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate chapter brief."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")
    await _check_ghostwriter_access(db, current_user.id)
    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    outline_ch = None
    if ws.outline and "chapters" in ws.outline:
        result = await db.execute(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order))
        ch_list = list(result.scalars().all())
        chapters = ws.outline["chapters"]
        for i, ch in enumerate(ch_list):
            if ch.id == chapter_id and i < len(chapters):
                outline_ch = chapters[i]
                break

    brief_text = await generate_chapter_brief(
        db, book_id, book.type or "general", chapter, ws, outline_ch
    )

    result = await db.execute(
        select(ChapterBrief).where(
            ChapterBrief.ghostwriter_workspace_id == ws.id,
            ChapterBrief.chapter_id == chapter_id,
        )
    )
    brief = result.scalar_one_or_none()
    if brief:
        brief.brief_text = brief_text
    else:
        brief = ChapterBrief(
            ghostwriter_workspace_id=ws.id,
            chapter_id=chapter_id,
            brief_text=brief_text,
            sort_order=chapter.sort_order,
        )
        db.add(brief)
    await db.flush()
    await db.refresh(brief)
    return {"brief_text": brief_text, "brief_id": str(brief.id)}


@router.post("/briefs/{chapter_id}/approve")
async def approve_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Approve chapter brief."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    result = await db.execute(
        select(ChapterBrief).where(
            ChapterBrief.ghostwriter_workspace_id == ws.id,
            ChapterBrief.chapter_id == chapter_id,
        )
    )
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found")
    brief.approved_at = datetime.now(timezone.utc)
    await db.flush()
    return {"approved": True}


@router.post("/draft/generate")
async def generate_draft(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: GenerateDraftRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate full chapter draft from brief. Returns draft content."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")
    await _check_ghostwriter_access(db, current_user.id)
    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    ws = await get_or_create_workspace(db, book_id)
    result = await db.execute(select(Chapter).where(Chapter.id == data.chapter_id, Chapter.book_id == book_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    brief_text = ""
    if data.use_brief:
        result = await db.execute(
            select(ChapterBrief).where(
                ChapterBrief.ghostwriter_workspace_id == ws.id,
                ChapterBrief.chapter_id == data.chapter_id,
            )
        )
        brief = result.scalar_one_or_none()
        if brief:
            brief_text = brief.brief_text
    if not brief_text:
        brief_text = f"Chapter: {chapter.title}. Write a full draft."

    draft_text = await generate_chapter_draft(
        db, book_id, book.type or "general", chapter, ws, brief_text
    )
    return {"draft_text": draft_text, "chapter_id": str(data.chapter_id)}


@router.post("/draft/apply")
async def apply_draft(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: ApplyDraftRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Apply generated draft to chapter. Sets content_source=ai_generated."""
    from authora.schemas.book import ChapterResponse

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == data.chapter_id, Chapter.book_id == book_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    content = plain_text_to_tiptap(data.draft_text)
    word_count = len(data.draft_text.split())

    # Save version before overwriting
    version = ChapterVersion(
        chapter_id=chapter.id,
        content=chapter.content,
        word_count=chapter.word_count,
        content_source=chapter.content_source,
        created_by=current_user.id,
    )
    db.add(version)
    chapter.content = content
    chapter.word_count = word_count
    chapter.content_source = "ai_generated"
    await db.flush()
    await db.refresh(chapter)
    return ChapterResponse.model_validate(chapter)


@router.post("/regenerate")
async def regenerate_section_endpoint(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: RegenerateSectionRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Regenerate a section with optional feedback. Streams response."""
    settings = get_settings()
    await _check_ghostwriter_access(db, current_user.id)
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")
    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    new_text = await regenerate_section(
        db, book_id, book.type or "general", data.selection, data.feedback
    )
    return {"text": new_text}


@router.post("/rewrite-with-feedback")
async def rewrite_with_feedback_endpoint(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: RewriteWithFeedbackRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Rewrite selection with user feedback."""
    settings = get_settings()
    await _check_ghostwriter_access(db, current_user.id)
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")
    if not check_rate_limit(str(current_user.id)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    new_text = await rewrite_with_feedback(
        db, book_id, book.type or "general", data.selection, data.feedback
    )
    return {"text": new_text}
