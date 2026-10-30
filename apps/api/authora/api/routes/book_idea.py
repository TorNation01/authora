"""Overall Book Idea routes - the first rung of the planning ladder."""

from __future__ import annotations

import uuid
from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.data.book_bible_schema import SECTIONS as BIBLE_SECTIONS
from authora.database import get_db
from authora.data.book_idea_schema import (
    SECTIONS,
    blank_sections,
    completeness,
    merge_sections,
    section_by_key,
)
from authora.models import BookBible, BookIdea, Chapter
from authora.services.ai import complete_sync

router = APIRouter(prefix="/projects", tags=["book-idea"])

Db = Annotated[AsyncSession, Depends(get_db)]




def _payload(idea: BookIdea) -> dict:
    sections = merge_sections(idea.sections, None)
    return {
        "book_id": idea.book_id,
        "sections": sections,
        "version": idea.version,
        "completeness": completeness(sections),
    }


async def _get_or_create(db: AsyncSession, book_id: uuid.UUID) -> BookIdea:
    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()
    if idea is None:
        idea = BookIdea(book_id=book_id, sections=blank_sections(), version=1)
        db.add(idea)
        await db.commit()
        await db.refresh(idea)
    return idea


class IdeaPatch(BaseModel):
    sections: dict[str, dict] = Field(default_factory=dict)


class DraftRequest(BaseModel):
    section: str
    field: str


class DraftResponse(BaseModel):
    text: str


@router.get("/book-idea/schema")
async def book_idea_schema():
    return {"sections": SECTIONS}


@router.get("/{project_id}/books/{book_id}/book-idea")
async def get_book_idea(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    return _payload(await _get_or_create(db, book_id))


@router.patch("/{project_id}/books/{book_id}/book-idea")
async def patch_book_idea(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: IdeaPatch,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    idea = await _get_or_create(db, book_id)
    idea.sections = merge_sections(idea.sections, payload.sections)
    idea.version = (idea.version or 1) + 1
    await db.commit()
    await db.refresh(idea)
    return _payload(idea)


def _bible_context(bible: BookBible | None) -> str:
    """Render the bible as readable text for the prompt."""
    if bible is None:
        return ""
    body = bible.sections or {}
    lines: list[str] = []
    for section in BIBLE_SECTIONS:
        data = body.get(section["key"]) or {}
        rendered: list[str] = []
        for field in section["fields"]:
            value = data.get(field["key"])
            if isinstance(value, list):
                for row in value:
                    if isinstance(row, dict):
                        cols = ", ".join(f"{k}: {v}" for k, v in row.items() if str(v or "").strip())
                        if cols:
                            rendered.append(f"- {field['label']}: {cols}")
                    elif str(row or "").strip():
                        rendered.append(f"- {field['label']}: {row}")
            elif str(value or "").strip():
                rendered.append(f"- {field['label']}: {value}")
        if rendered:
            lines.append(f"{section['title']}:\n" + "\n".join(rendered))
    return "\n\n".join(lines)


@router.post(
    "/{project_id}/books/{book_id}/book-idea/draft-field",
    response_model=DraftResponse,
)
async def draft_idea_field(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: DraftRequest,
    current_user: CurrentUser,
    db: Db,
):
    """Draft one answer, grounded in the bible and whatever this sheet already says.

    Returns text only - it does not save. The author accepts or ignores it.
    """
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    idea = await _get_or_create(db, book_id)

    section = section_by_key(data.section)
    if section is None:
        raise HTTPException(status_code=400, detail="Unknown section")
    field = next((f for f in section["fields"] if f["key"] == data.field), None)
    if field is None:
        raise HTTPException(status_code=400, detail="Unknown field")
    if field["type"] not in ("text", "short", "list"):
        raise HTTPException(status_code=400, detail="Only text, short and list fields can be drafted")

    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    bible_text = _bible_context(bible)[:12000]

    written: list[str] = []
    for key, values in (idea.sections or {}).items():
        other = section_by_key(key)
        if other is None:
            continue
        for f in other["fields"]:
            value = (values or {}).get(f["key"])
            if isinstance(value, list):
                value = "; ".join(str(v) for v in value if str(v).strip())
            if isinstance(value, str) and value.strip() and not (key == data.section and f["key"] == data.field):
                written.append(f"{f['label']}: {value.strip()}")
    written_text = "\n".join(written)[:8000]

    chapters = (
        await db.execute(
            select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order).limit(40)
        )
    ).scalars().all()
    chapter_text = ", ".join(f"{c.sort_order}. {c.title}" for c in chapters) or "(no chapters yet)"

    shape = (
        "Reply with the points only, one per line, each starting with '- '."
        if field["type"] == "list"
        else "Reply with the answer only: no preamble, no headings, no quotation marks."
    )

    prompt = f"""You are helping an author think through the overall idea of a book, before it is written.

BOOK: {book.title}

WHAT THE AUTHOR HAS ALREADY WRITTEN ON THIS SHEET:
{written_text or "(nothing yet)"}

BOOK BIBLE (established facts - do not contradict these):
{bible_text or "(not written yet)"}

CHAPTERS PLANNED: {chapter_text}

Answer this one question, in the author's voice, for this book:
{field['label']} - {field['prompt']}

Do not invent proper nouns that are not already in the material above. If the material genuinely does not support a specific answer, write a concrete proposal and mark it as a proposal. {shape}"""
    system = (
        "You are a sharp, unsentimental story editor who works only from the author's own material. "
        "You never pad, never flatter, and never invent facts about their book."
    )

    try:
        text = await complete_sync(prompt, system, max_tokens=700)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"AI drafting unavailable: {exc}") from exc

    return DraftResponse(text=(text or "").strip())
