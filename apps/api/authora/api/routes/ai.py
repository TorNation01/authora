"""AI assistance API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.models import Book, Chapter, Project
from authora.services.ai_service import complete_stream

router = APIRouter(prefix="/ai", tags=["ai"])

WRITING_SYSTEM = """You are an expert writing assistant for AUTHORA, an AI-powered book builder.
You help fiction and non-fiction authors with:
- Generating prose, dialogue, and descriptions
- Expanding outlines into full scenes
- Suggesting edits and improvements
- Overcoming writer's block
- Maintaining tone and voice consistency

Be supportive, creative, and concise. Match the author's style when they provide context."""


class AICompleteRequest(BaseModel):
    prompt: str
    context: str | None = None
    chapter_id: uuid.UUID | None = None
    book_id: uuid.UUID | None = None
    max_tokens: int = 2048


async def _get_book_or_404(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book | None:
    result = await db.execute(
        select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


@router.post("/complete")
async def ai_complete_stream(
    data: AICompleteRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Stream AI completion for writing assistance."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    system = WRITING_SYSTEM
    if data.context:
        system += f"\n\nRelevant context:\n{data.context}"

    if data.chapter_id and data.book_id:
        result = await db.execute(
            select(Chapter).options(selectinload(Chapter.book)).where(
                Chapter.id == data.chapter_id,
                Chapter.book_id == data.book_id,
            )
        )
        ch = result.scalar_one_or_none()
        if ch and ch.book:
            proj = await db.get(Project, ch.book.project_id)
            if proj and proj.user_id == current_user.id:
                from authora.services.export import tiptap_to_plain_text
                recent = tiptap_to_plain_text(ch.content)[-2000:]
                if recent:
                    system += f"\n\nCurrent chapter content (end):\n{recent}"

    async def generate():
        async for chunk in complete_stream(data.prompt, system, data.max_tokens):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
