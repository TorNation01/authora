"""Chapter brief API - the 13-section planning document for a single chapter.

Additive routes under /projects. The existing ghostwriter brief endpoints are
untouched: this is the author-facing brief that a draft or a ghostwriter packet
is generated from.
"""

import json
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_project_or_404
from authora.data.book_bible_schema import SECTIONS as BIBLE_SECTIONS
from authora.data.chapter_brief_schema import (
    SECTIONS,
    blank_sections,
    completeness,
    merge_sections,
    section_by_key,
)
from authora.database import get_db
from authora.models import Act, BookBible, Chapter, ChapterBriefSheet
from authora.services.ai import complete_sync

router = APIRouter(prefix="/projects", tags=["chapter-brief"])

Db = Annotated[AsyncSession, Depends(get_db)]


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class BriefUpdate(BaseModel):
    sections: dict[str, Any] = Field(default_factory=dict)
    section_status: dict[str, str] | None = None


class BriefResponse(BaseModel):
    chapter_id: uuid.UUID
    book_id: uuid.UUID
    sections: dict[str, Any]
    section_status: dict[str, str]
    version: int
    updated_at: datetime | None = None
    completeness: dict[str, Any]


class BriefListItem(BaseModel):
    chapter_id: uuid.UUID
    title: str
    sort_order: int
    act_id: uuid.UUID | None = None
    act_title: str | None = None
    word_count: int | None = None
    pct: int = 0
    filled: int = 0
    total: int = 0
    updated_at: datetime | None = None


class DraftRequest(BaseModel):
    section: str
    field: str
    instruction: str | None = None


class DraftResponse(BaseModel):
    section: str
    field: str
    text: str


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
async def _get_chapter(db: AsyncSession, book_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter:
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    chapter = result.scalar_one_or_none()
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


async def _get_or_create_brief(db: AsyncSession, book_id: uuid.UUID, chapter_id: uuid.UUID) -> ChapterBriefSheet:
    result = await db.execute(
        select(ChapterBriefSheet).where(ChapterBriefSheet.chapter_id == chapter_id)
    )
    brief = result.scalar_one_or_none()
    if brief is None:
        brief = ChapterBriefSheet(book_id=book_id, chapter_id=chapter_id, sections=blank_sections(), section_status={})
        db.add(brief)
        await db.commit()
        await db.refresh(brief)
    else:
        merged = merge_sections(blank_sections(), brief.sections or {})
        if merged != (brief.sections or {}):
            brief.sections = merged
            await db.commit()
            await db.refresh(brief)
    return brief


def _payload(brief: ChapterBriefSheet) -> BriefResponse:
    sections = brief.sections or {}
    return BriefResponse(
        chapter_id=brief.chapter_id,
        book_id=brief.book_id,
        sections=sections,
        section_status=brief.section_status or {},
        version=brief.version,
        updated_at=brief.updated_at,
        completeness=completeness(sections),
    )


def _bible_flat(bible: BookBible | None) -> dict[str, Any]:
    """Flatten the bible into {section.key: {field: value}} for prompting."""
    if bible is None:
        return {}
    return bible.sections or {}


def _brief_context(brief: ChapterBriefSheet) -> str:
    """Render the brief as readable text, so the AI can build on what is there."""
    lines: list[str] = []
    for section in SECTIONS:
        body = (brief.sections or {}).get(section["key"]) or {}
        rendered: list[str] = []
        for field in section["fields"]:
            value = body.get(field["key"])
            if field["type"] == "list" and isinstance(value, list):
                if value:
                    rendered.append(f"- {field['label']}: " + "; ".join(str(v) for v in value))
            elif field["type"] == "rows" and isinstance(value, list):
                for row in value:
                    if isinstance(row, dict) and any(str(v).strip() for v in row.values()):
                        cols = ", ".join(f"{k}: {v}" for k, v in row.items() if str(v or "").strip())
                        rendered.append(f"- {field['label']}: {cols}")
            elif field["type"] == "checks":
                if isinstance(value, dict) and value:
                    rendered.append(f"- {field['label']}: " + ", ".join(f"{k} = {v}" for k, v in value.items()))
            elif str(value or "").strip():
                rendered.append(f"- {field['label']}: {value}")
        if rendered:
            lines.append(f"{section['title']}:\n" + "\n".join(rendered))
    return "\n\n".join(lines)


def _bible_context(bible: BookBible | None) -> str:
    body = _bible_flat(bible)
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


# --------------------------------------------------------------------------- #
# Static route first, so it is not swallowed by the UUID path parameter
# --------------------------------------------------------------------------- #
@router.get("/chapter-brief/schema")
async def chapter_brief_schema(_: CurrentUser):
    """The 13-section chapter brief questionnaire the web app renders."""
    return {"sections": SECTIONS}


# --------------------------------------------------------------------------- #
# Per-chapter brief
# --------------------------------------------------------------------------- #
@router.get("/{project_id}/books/{book_id}/chapter-briefs", response_model=list[BriefListItem])
async def list_briefs(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    """Every chapter in the book with how complete its brief is."""
    await get_book_or_404(db, book_id, current_user.id, project_id)

    chapters = (
        await db.execute(
            select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order, Chapter.created_at)
        )
    ).scalars().all()
    briefs = (
        await db.execute(select(ChapterBriefSheet).where(ChapterBriefSheet.book_id == book_id))
    ).scalars().all()
    by_chapter = {b.chapter_id: b for b in briefs}

    acts = (await db.execute(select(Act).where(Act.book_id == book_id))).scalars().all()
    act_titles = {a.id: a.title for a in acts}

    out: list[BriefListItem] = []
    for index, chapter in enumerate(chapters, start=1):
        brief = by_chapter.get(chapter.id)
        stats = completeness(brief.sections or {} if brief else blank_sections())
        out.append(
            BriefListItem(
                chapter_id=chapter.id,
                title=chapter.title or f"Chapter {index}",
                sort_order=chapter.sort_order or index,
                act_id=getattr(chapter, "act_id", None),
                act_title=act_titles.get(getattr(chapter, "act_id", None)),
                word_count=getattr(chapter, "word_count", None),
                pct=stats["pct"],
                filled=stats["filled"],
                total=stats["total"],
                updated_at=brief.updated_at if brief else None,
            )
        )
    return out


@router.get("/{project_id}/books/{book_id}/chapter-briefs/{chapter_id}", response_model=BriefResponse)
async def get_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await _get_chapter(db, book_id, chapter_id)
    brief = await _get_or_create_brief(db, book_id, chapter_id)
    return _payload(brief)


@router.patch("/{project_id}/books/{book_id}/chapter-briefs/{chapter_id}", response_model=BriefResponse)
async def update_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: BriefUpdate,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await _get_chapter(db, book_id, chapter_id)
    brief = await _get_or_create_brief(db, book_id, chapter_id)

    brief.sections = merge_sections(brief.sections or {}, data.sections or {})
    if data.section_status is not None:
        current = dict(brief.section_status or {})
        valid = {s["key"] for s in SECTIONS}
        for key, value in data.section_status.items():
            if key in valid and value in ("working", "locked", "undecided", ""):
                if value:
                    current[key] = value
                else:
                    current.pop(key, None)
        brief.section_status = current
    brief.version = (brief.version or 1) + 1
    await db.commit()
    await db.refresh(brief)
    return _payload(brief)


@router.post("/{project_id}/books/{book_id}/chapter-briefs/{chapter_id}/prefill", response_model=BriefResponse)
async def prefill_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    """Fill the identity block from the book, its bible and its acts.

    Only empty fields are filled - anything the author has typed wins.
    """
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await _get_chapter(db, book_id, chapter_id)
    brief = await _get_or_create_brief(db, book_id, chapter_id)

    bible = (
        await db.execute(select(BookBible).where(BookBible.book_id == book_id))
    ).scalar_one_or_none()
    bible_sections = (bible.sections or {}) if bible else {}
    details = bible_sections.get("book_details") or {}
    narrative = bible_sections.get("narrative_format") or {}

    chapters = (
        await db.execute(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order))
    ).scalars().all()
    number = next((i for i, c in enumerate(chapters, start=1) if c.id == chapter.id), 1)

    act_title = ""
    act_id = getattr(chapter, "act_id", None)
    if act_id:
        act = (await db.execute(select(Act).where(Act.id == act_id))).scalar_one_or_none()
        act_title = act.title if act else ""

    candidates = {
        "book": book.title or "",
        "series": details.get("series") or "",
        "chapter_number": str(number),
        "working_title": chapter.title or "",
        "position_in_story": act_title or details.get("series_position") or "",
        "pov": narrative.get("point_of_view") or "",
        "tense": narrative.get("tense") or "",
        "location": getattr(chapter, "location", "") or "",
        "length_guidance": details.get("preferred_length") or "",
    }

    sections = dict(brief.sections or {})
    identity = dict(sections.get("identity") or {})
    filled_any = False
    for key, value in candidates.items():
        if value and not str(identity.get(key) or "").strip():
            identity[key] = value
            filled_any = True
    sections["identity"] = identity
    if filled_any:
        brief.sections = sections
        brief.version = (brief.version or 1) + 1
        await db.commit()
        await db.refresh(brief)
    return _payload(brief)


@router.post(
    "/{project_id}/books/{book_id}/chapter-briefs/{chapter_id}/draft-field",
    response_model=DraftResponse,
)
async def draft_field(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: DraftRequest,
    current_user: CurrentUser,
    db: Db,
):
    """Draft one brief field with AI, grounded in the bible and the brief so far.

    Returns the text; it does not save. The author accepts or ignores it.
    """
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await _get_chapter(db, book_id, chapter_id)
    brief = await _get_or_create_brief(db, book_id, chapter_id)

    section = section_by_key(data.section)
    if section is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown section")
    field = next((f for f in section["fields"] if f["key"] == data.field), None)
    if field is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown field")
    if field["type"] not in ("text", "short", "list"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only text, short and list fields can be drafted",
        )

    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    bible_text = _bible_context(bible)[:12000]
    brief_text = _brief_context(brief)[:8000]

    shape = (
        "Reply with the bullet items only, one per line, each starting with '- '."
        if field["type"] == "list"
        else "Reply with the finished text only: no preamble, no headings, no quotation marks."
    )

    prompt = f"""You are helping an author plan one chapter of a book.

BOOK BIBLE (the whole book's established facts):
{bible_text or "(not written yet)"}

CHAPTER: {chapter.title or 'Untitled'}

BRIEF SO FAR:
{brief_text or "(empty)"}

TASK: Draft the "{field['label']}" field for section {section['number']}. {section['title']}.
What this field asks for: {field.get('prompt', '')}
{f"Extra instruction from the author: {data.instruction}" if data.instruction else ""}

Rules:
- Stay inside the bible. Do not invent names, places or facts that contradict it.
- Be specific and concrete. No generic writing advice, no filler.
- {shape}"""

    system = (
        "You are a precise story editor and ghostwriting assistant. "
        "You write planning documents, not prose. You never contradict established canon."
    )

    try:
        text = await complete_sync(prompt, system, max_tokens=900)
    except Exception as exc:  # provider not configured, quota, network
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI unavailable: {exc}",
        ) from exc

    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return DraftResponse(section=data.section, field=data.field, text=cleaned)


@router.delete(
    "/{project_id}/books/{book_id}/chapter-briefs/{chapter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_brief(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    """Clear a brief back to blank (the chapter itself is untouched)."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await _get_chapter(db, book_id, chapter_id)
    result = await db.execute(select(ChapterBriefSheet).where(ChapterBriefSheet.chapter_id == chapter_id))
    brief = result.scalar_one_or_none()
    if brief is not None:
        await db.delete(brief)
        await db.commit()
    return None
