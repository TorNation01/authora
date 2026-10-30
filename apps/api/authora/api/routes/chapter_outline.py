"""Chapter Outline - the chapter-by-chapter map."""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.data.book_bible_schema import SECTIONS as BIBLE_SECTIONS
from authora.data.book_idea_schema import SECTIONS as IDEA_SECTIONS
from authora.data.chapter_outline_schema import (
    FIELDS,
    FIELD_BY_KEY,
    SECTIONS,
    blank_sections,
    completeness,
    normalise,
)
from authora.database import get_db
from authora.models import BookBible, BookIdea, Chapter, ChapterOutline, OutlineTurningPoint
from authora.services.ai import complete_sync

router = APIRouter(prefix="/projects", tags=["chapter-outline"])

Db = Annotated[AsyncSession, Depends(get_db)]


class PatchIn(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)
    section_key: str | None = None
    turning_point_id: uuid.UUID | None = None


class DraftRequest(BaseModel):
    field: str


class DraftResponse(BaseModel):
    text: str


def _payload(outline: ChapterOutline | None) -> dict[str, Any] | None:
    if outline is None:
        return None
    body = normalise(outline.sections)
    stats = completeness(body)
    return {
        "id": str(outline.id),
        "sections": body,
        "filled": stats["filled"],
        "total": stats["total"],
        "version": outline.version,
        "turning_point_id": str(outline.turning_point_id) if outline.turning_point_id else None,
    }


@router.get("/chapter-outline/schema")
async def chapter_outline_schema():
    return {"sections": SECTIONS, "total": len(FIELDS)}


@router.get("/{project_id}/books/{book_id}/chapter-outline")
async def list_chapter_outlines(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)

    chapters = (
        await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
            .order_by(Chapter.sort_order)
        )
    ).scalars().all()

    outlines = {
        row.chapter_id: row
        for row in (
            await db.execute(select(ChapterOutline).where(ChapterOutline.book_id == book_id))
        ).scalars().all()
    }

    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order)
        )
    ).scalars().all()

    rows = []
    total = 0
    filled = 0
    for index, chapter in enumerate(chapters):
        outline = outlines.get(chapter.id)
        entry = _payload(outline)
        rows.append(
            {
                "chapter_id": str(chapter.id),
                "title": chapter.title,
                "sort_order": chapter.sort_order,
                "number": index + 1,
                "act_id": str(chapter.act_id) if chapter.act_id else None,
                "outline": entry,
            }
        )
        total += len(FIELDS)
        filled += entry["filled"] if entry else 0

    return {
        "book_id": str(book.id),
        "book_title": book.title,
        "chapters": rows,
        "turning_points": [
            {"id": str(p.id), "title": p.title, "sort_order": p.sort_order} for p in points
        ],
        "progress": {
            "filled": filled,
            "total": total,
            "pct": round(filled / total * 100) if total else 0,
            "chapters": len(chapters),
        },
    }


async def _chapter_or_404(db: AsyncSession, chapter_id: uuid.UUID, book_id: uuid.UUID) -> Chapter:
    chapter = await db.get(Chapter, chapter_id)
    if chapter is None or chapter.book_id != book_id or chapter.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


async def _outline_for(db: AsyncSession, chapter: Chapter) -> ChapterOutline:
    outline = (
        await db.execute(select(ChapterOutline).where(ChapterOutline.chapter_id == chapter.id))
    ).scalar_one_or_none()
    if outline is None:
        outline = ChapterOutline(
            book_id=chapter.book_id,
            chapter_id=chapter.id,
            sections=blank_sections(),
            version=1,
        )
        db.add(outline)
        await db.flush()
    return outline


@router.patch("/{project_id}/books/{book_id}/chapter-outline/{chapter_id}")
async def patch_chapter_outline(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    payload: PatchIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await _chapter_or_404(db, chapter_id, book_id)
    outline = await _outline_for(db, chapter)

    body = normalise(outline.sections)
    for key, value in payload.fields.items():
        entry = FIELD_BY_KEY.get(key)
        if entry is None:
            continue
        section = next(s for s in SECTIONS if any(f["key"] == key for f in s["fields"]))
        body[section["key"]][key] = value
    outline.sections = body
    if payload.turning_point_id is not None:
        outline.turning_point_id = payload.turning_point_id
    outline.version = (outline.version or 1) + 1

    await db.commit()
    await db.refresh(outline)
    return _payload(outline)


@router.post(
    "/{project_id}/books/{book_id}/chapter-outline/{chapter_id}/draft-field",
    response_model=DraftResponse,
)
async def draft_chapter_outline_field(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    payload: DraftRequest,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await _chapter_or_404(db, chapter_id, book_id)
    outline = await _outline_for(db, chapter)

    field = FIELD_BY_KEY.get(payload.field)
    if field is None:
        raise HTTPException(status_code=400, detail="Unknown field")
    if not field.get("ai"):
        raise HTTPException(status_code=400, detail="That field is yours to decide")

    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()

    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order)
        )
    ).scalars().all()
    spine = "\n".join(
        f"{p.sort_order + 1}. {p.title}"
        + (f" - {p.fields.get('what_happens', '')[:180]}" if p.fields else "")
        for p in points
    )

    chapters = (
        await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
            .order_by(Chapter.sort_order)
        )
    ).scalars().all()
    index = next((i for i, c in enumerate(chapters) if c.id == chapter.id), 0)

    neighbours = []
    for other in chapters[max(0, index - 2) : index + 3]:
        if other.id == chapter.id:
            continue
        neighbour_outline = (
            await db.execute(select(ChapterOutline).where(ChapterOutline.chapter_id == other.id))
        ).scalar_one_or_none()
        purpose = ""
        if neighbour_outline:
            purpose = str(normalise(neighbour_outline.sections)["purpose"]["purpose"] or "")
        neighbours.append(f"- {other.title}: {purpose[:160] or '(no purpose written)'}")

    body = normalise(outline.sections)
    current = "\n".join(
        f"- {FIELD_BY_KEY[k]['label']}: {v}"
        for section in SECTIONS
        for k, v in body[section["key"]].items()
        if k in FIELD_BY_KEY and str(v or "").strip() and k != payload.field
    )

    def render(sections_data: dict[str, Any], schema: list[dict[str, Any]], limit: int) -> str:
        lines: list[str] = []
        for section in schema:
            section_body = (sections_data or {}).get(section["key"]) or {}
            bits: list[str] = []
            for item in section["fields"]:
                value = section_body.get(item["key"])
                if isinstance(value, list):
                    rows = [str(v) for v in value if str(v or "").strip()]
                    if rows:
                        bits.append(f"- {item['label']}: " + "; ".join(rows))
                elif str(value or "").strip():
                    bits.append(f"- {item['label']}: {value}")
            if bits:
                lines.append(f"{section['title']}:\n" + "\n".join(bits))
        return "\n\n".join(lines)[:limit]

    idea_text = render(idea.sections if idea else {}, IDEA_SECTIONS, 6000)
    bible_text = render(bible.sections if bible else {}, BIBLE_SECTIONS, 8000)
    locked = [
        section["title"]
        for section in BIBLE_SECTIONS
        if (bible.section_status or {}).get(section["key"]) == "locked"
    ]

    shape = (
        "Reply with the points only, one per line, each starting with '- '."
        if field["type"] == "list"
        else "Reply with the answer only: no preamble, no headings, no quotation marks."
    )

    prompt = f"""You are helping an author map a novel chapter by chapter, before the prose exists.

BOOK: {book.title}
CHAPTER {index + 1} OF {len(chapters)}: {chapter.title}

THE BOOK IDEA:
{idea_text or "(not written yet)"}

THE BOOK BIBLE (established facts - never contradict these):
LOCKED CANON - sealed decisions, do not revise or contradict: {', '.join(locked) if locked else '(none marked locked yet)'}
{bible_text or "(not written yet)"}

THE OVERALL OUTLINE (the spine this chapter must serve):
{spine or "(no turning points written yet)"}

NEIGHBOURING CHAPTERS:
{chr(10).join(neighbours) or "(this is the first or only chapter)"}

ALREADY WRITTEN ON THIS CHAPTER:
{current or "(nothing yet)"}

Answer this one question for this chapter:
{field['label']} - {field['prompt']}

This is a map, not prose: concrete, brief, no scene-writing. Stay inside the established facts and do not invent proper nouns, places or characters that are not already in the material. If the material does not support a specific answer, make a concrete proposal and mark it as a proposal. {shape}"""
    system = (
        "You are a structural story editor mapping a novel chapter by chapter. "
        "You think in cause and effect, you cut chapters that have no job, and you never invent "
        "facts about the author's book."
    )

    try:
        text = await complete_sync(prompt, system, max_tokens=500)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"AI drafting unavailable: {exc}") from exc

    return DraftResponse(text=(text or "").strip())
