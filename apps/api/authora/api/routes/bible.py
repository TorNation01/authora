"""Book Bible, character library and acts API.

Additive routes. Existing fiction_* endpoints are untouched.
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_project_or_404
from authora.data.book_bible_schema import (
    SECTIONS,
    blank_sections,
    completeness,
    merge_sections,
    sections_for_scope,
)
from authora.database import get_db
from authora.models import (
    Act,
    Book,
    BookBible,
    BookCharacter,
    Chapter,
    Character,
    CharacterBond,
)

router = APIRouter(prefix="/projects", tags=["bible"])

Db = Annotated[AsyncSession, Depends(get_db)]


# --------------------------------------------------------------------------- #
# Book Bible
# --------------------------------------------------------------------------- #
class BibleUpdate(BaseModel):
    sections: dict[str, Any] = Field(default_factory=dict)
    section_status: dict[str, str] | None = None


class BibleResponse(BaseModel):
    book_id: uuid.UUID
    sections: dict[str, Any]
    section_status: dict[str, str]
    version: int
    updated_at: datetime | None = None
    completeness: dict[str, Any]


async def _get_or_create_bible(db: AsyncSession, book_id: uuid.UUID) -> BookBible:
    result = await db.execute(select(BookBible).where(BookBible.book_id == book_id))
    bible = result.scalar_one_or_none()
    if bible is None:
        bible = BookBible(book_id=book_id, sections=blank_sections(), section_status={})
        db.add(bible)
        await db.commit()
        await db.refresh(bible)
    else:
        # Backfill any section or field added to the schema since this bible was created.
        merged = merge_sections(blank_sections(), bible.sections or {})
        if merged != (bible.sections or {}):
            bible.sections = merged
            await db.commit()
            await db.refresh(bible)
    return bible


def _bible_payload(bible: BookBible, scope: str | None = None) -> BibleResponse:
    schema = sections_for_scope(scope)
    allowed = {section["key"] for section in schema}
    sections = {k: v for k, v in (bible.sections or {}).items() if k in allowed}
    return BibleResponse(
        book_id=bible.book_id,
        sections=sections,
        section_status={k: v for k, v in (bible.section_status or {}).items() if k in allowed},
        version=bible.version,
        updated_at=bible.updated_at,
        completeness=completeness(sections, schema),
    )


@router.get("/bible/schema")
async def bible_schema(_: CurrentUser, scope: str | None = None):
    """The questionnaire the web app renders - scope-aware for standalone books."""
    return {"sections": sections_for_scope(scope), "scope": scope or "series"}


@router.get("/{project_id}/books/{book_id}/bible", response_model=BibleResponse)
async def get_bible(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    project = await get_project_or_404(db, project_id, current_user.id)
    await get_book_or_404(db, book_id, current_user.id, project_id)
    bible = await _get_or_create_bible(db, book_id)
    return _bible_payload(bible, getattr(project, "scope", None))


@router.patch("/{project_id}/books/{book_id}/bible", response_model=BibleResponse)
async def update_bible(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: BibleUpdate,
    current_user: CurrentUser,
    db: Db,
):
    project = await get_project_or_404(db, project_id, current_user.id)
    await get_book_or_404(db, book_id, current_user.id, project_id)
    bible = await _get_or_create_bible(db, book_id)

    merged = merge_sections(bible.sections or {}, payload.sections or {})
    status_map = dict(bible.section_status or {})
    if payload.section_status:
        valid = {s["key"] for s in SECTIONS}
        for key, value in payload.section_status.items():
            if key in valid and value in ("working", "locked", "undecided"):
                status_map[key] = value

    bible.sections = merged
    bible.section_status = status_map
    bible.version = (bible.version or 1) + 1
    await db.commit()
    await db.refresh(bible)
    return _bible_payload(bible, getattr(project, "scope", None))


# --------------------------------------------------------------------------- #
# Character library
# --------------------------------------------------------------------------- #
CHARACTER_FIELDS = (
    "name", "aliases", "role", "archetype", "one_line", "age", "pronouns",
    "gender", "profession", "appearance", "voice", "personality", "goals", "fears", "motivations",
    "internal_conflict", "external_conflict", "backstory", "wound", "secret",
    "arc_summary", "quirks", "need", "flaws", "skills_limitations", "values_boundaries",
    "distinctive_behaviour", "portrait_url", "portrait_source", "portrait_updated_at",
    "dialogue_patterns", "relationships_notes",
    "private_notes", "canon_status", "status", "extras", "sort_order",
)


class CharacterIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    aliases: list[str] = Field(default_factory=list)
    role: str = "supporting"
    archetype: str | None = None
    one_line: str | None = None
    age: str | None = None
    pronouns: str | None = None
    gender: str | None = None
    profession: str | None = None
    appearance: str | None = None
    voice: str | None = None
    personality: str | None = None
    goals: str | None = None
    fears: str | None = None
    motivations: str | None = None
    internal_conflict: str | None = None
    external_conflict: str | None = None
    backstory: str | None = None
    wound: str | None = None
    secret: str | None = None
    arc_summary: str | None = None
    quirks: str | None = None
    need: str | None = None
    flaws: str | None = None
    skills_limitations: str | None = None
    values_boundaries: str | None = None
    distinctive_behaviour: str | None = None
    portrait_url: str | None = None
    portrait_source: str | None = None
    portrait_updated_at: datetime | None = None
    dialogue_patterns: str | None = None
    relationships_notes: str | None = None
    private_notes: str | None = None
    canon_status: str = "working"
    status: str = "active"
    extras: dict[str, Any] = Field(default_factory=dict)
    origin_book_id: uuid.UUID | None = None
    continuation_of: uuid.UUID | None = None


class CharacterPatch(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)


class CharacterOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    origin_book_id: uuid.UUID | None = None
    continuation_of: uuid.UUID | None = None
    name: str
    aliases: list[str] = Field(default_factory=list)
    role: str
    archetype: str | None = None
    one_line: str | None = None
    age: str | None = None
    pronouns: str | None = None
    gender: str | None = None
    profession: str | None = None
    appearance: str | None = None
    voice: str | None = None
    personality: str | None = None
    goals: str | None = None
    fears: str | None = None
    motivations: str | None = None
    internal_conflict: str | None = None
    external_conflict: str | None = None
    backstory: str | None = None
    wound: str | None = None
    secret: str | None = None
    arc_summary: str | None = None
    quirks: str | None = None
    need: str | None = None
    flaws: str | None = None
    skills_limitations: str | None = None
    values_boundaries: str | None = None
    distinctive_behaviour: str | None = None
    portrait_url: str | None = None
    portrait_source: str | None = None
    portrait_updated_at: datetime | None = None
    dialogue_patterns: str | None = None
    relationships_notes: str | None = None
    private_notes: str | None = None
    canon_status: str
    status: str
    extras: dict[str, Any] = Field(default_factory=dict)
    sort_order: int = 0
    books: list[dict[str, Any]] = Field(default_factory=list)
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


def _character_out(c: Character, books: list[dict[str, Any]] | None = None) -> CharacterOut:
    data = {name: getattr(c, name) for name in CHARACTER_FIELDS}
    data["aliases"] = data.get("aliases") or []
    data["extras"] = data.get("extras") or {}
    return CharacterOut(
        id=c.id, project_id=c.project_id, origin_book_id=c.origin_book_id,
        continuation_of=c.continuation_of, books=books or [], updated_at=c.updated_at, **data,
    )


@router.get("/{project_id}/characters")
async def list_characters(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
    q: str | None = Query(None, description="Search name, alias or one-line"),
    role: str | None = Query(None),
    include_retired: bool = Query(False),
):
    await get_project_or_404(db, project_id, current_user.id)
    stmt = select(Character).where(
        Character.project_id == project_id, Character.deleted_at.is_(None)
    )
    if not include_retired:
        stmt = stmt.where(Character.status == "active")
    if role:
        stmt = stmt.where(Character.role == role)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Character.name).like(like),
                func.lower(func.coalesce(Character.one_line, "")).like(like),
                func.lower(func.coalesce(Character.archetype, "")).like(like),
            )
        )
    stmt = stmt.order_by(Character.sort_order, func.lower(Character.name))
    rows = (await db.execute(stmt)).scalars().all()

    links = (await db.execute(
        select(BookCharacter.character_id, Book.id, Book.title)
        .join(Book, Book.id == BookCharacter.book_id)
        .where(BookCharacter.character_id.in_([c.id for c in rows] or [uuid.uuid4()]))
    )).all() if rows else []
    by_char: dict[uuid.UUID, list[dict[str, Any]]] = {}
    for cid, bid, title in links:
        by_char.setdefault(cid, []).append({"id": str(bid), "title": title})

    return {"characters": [_character_out(c, by_char.get(c.id, [])).model_dump() for c in rows]}


@router.get("/{project_id}/characters/name-check")
async def name_check(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
    name: str = Query(..., min_length=1),
    exclude_id: uuid.UUID | None = Query(None),
):
    """Has this name already been used anywhere in the project?"""
    await get_project_or_404(db, project_id, current_user.id)
    needle = name.strip().lower()
    stmt = select(Character).where(
        Character.project_id == project_id,
        Character.deleted_at.is_(None),
        func.lower(Character.name) == needle,
    )
    if exclude_id:
        stmt = stmt.where(Character.id != exclude_id)
    match = (await db.execute(stmt)).scalars().all()

    alias_match: list[Character] = []
    if not match:
        all_chars = (await db.execute(
            select(Character).where(Character.project_id == project_id, Character.deleted_at.is_(None))
        )).scalars().all()
        alias_match = [
            c for c in all_chars
            if any((a or "").strip().lower() == needle for a in (c.aliases or []))
            and (not exclude_id or c.id != exclude_id)
        ]

    hits = match or alias_match
    return {
        "name": name,
        "used": bool(hits),
        "exact": bool(match),
        "matches": [
            {"id": str(c.id), "name": c.name, "role": c.role, "continuation_of": str(c.continuation_of) if c.continuation_of else None}
            for c in hits
        ],
    }


@router.post("/{project_id}/characters", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: uuid.UUID,
    payload: CharacterIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    if payload.origin_book_id:
        await get_book_or_404(db, payload.origin_book_id, current_user.id, project_id)
    if payload.continuation_of:
        parent = await db.get(Character, payload.continuation_of)
        if not parent or parent.project_id != project_id:
            raise HTTPException(status_code=404, detail="Character to continue not found")

    char = Character(project_id=project_id, **payload.model_dump())
    db.add(char)
    await db.commit()
    await db.refresh(char)
    if payload.origin_book_id:
        db.add(BookCharacter(book_id=payload.origin_book_id, character_id=char.id, role_in_book=payload.role))
        await db.commit()
    return _character_out(char)


@router.get("/{project_id}/characters/{character_id}", response_model=CharacterOut)
async def get_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id or char.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Character not found")
    return _character_out(char)


@router.patch("/{project_id}/characters/{character_id}", response_model=CharacterOut)
async def update_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    payload: CharacterPatch,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id or char.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Character not found")

    for key, value in (payload.fields or {}).items():
        if key in CHARACTER_FIELDS:
            setattr(char, key, value)
    if not (char.name or "").strip():
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    await db.commit()
    await db.refresh(char)
    return _character_out(char)


@router.delete("/{project_id}/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id or char.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Character not found")
    char.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


@router.post("/{project_id}/books/{book_id}/characters/{character_id}", status_code=status.HTTP_201_CREATED)
async def attach_character_to_book(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
    role_in_book: str | None = Query(None),
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id:
        raise HTTPException(status_code=404, detail="Character not found")
    existing = (await db.execute(
        select(BookCharacter).where(
            BookCharacter.book_id == book_id, BookCharacter.character_id == character_id
        )
    )).scalar_one_or_none()
    if existing:
        return {"attached": True, "id": str(existing.id)}
    link = BookCharacter(book_id=book_id, character_id=character_id, role_in_book=role_in_book)
    db.add(link)
    await db.commit()
    return {"attached": True, "id": str(link.id)}


@router.delete("/{project_id}/books/{book_id}/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_character_from_book(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    link = (await db.execute(
        select(BookCharacter).where(
            BookCharacter.book_id == book_id, BookCharacter.character_id == character_id
        )
    )).scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
    return None


# --------------------------------------------------------------------------- #
# Acts
# --------------------------------------------------------------------------- #
class ActIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str | None = None
    color: str | None = None
    target_words: int | None = None


class ActPatch(BaseModel):
    title: str | None = None
    summary: str | None = None
    color: str | None = None
    target_words: int | None = None
    sort_order: int | None = None


class ReorderIn(BaseModel):
    order: list[uuid.UUID]


DEFAULT_ACTS = [("Act 1", "Setup and the inciting incident."),
                ("Act 2", "Confrontation and escalation."),
                ("Act 3", "Crisis, climax and resolution.")]


async def _ensure_acts(db: AsyncSession, book_id: uuid.UUID) -> list[Act]:
    rows = (await db.execute(
        select(Act).where(Act.book_id == book_id).order_by(Act.sort_order, Act.created_at)
    )).scalars().all()
    if rows:
        return list(rows)
    for i, (title, summary) in enumerate(DEFAULT_ACTS):
        db.add(Act(book_id=book_id, title=title, summary=summary, sort_order=i))
    await db.commit()
    return list((await db.execute(
        select(Act).where(Act.book_id == book_id).order_by(Act.sort_order)
    )).scalars().all())


@router.get("/{project_id}/books/{book_id}/acts")
async def list_acts(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    acts = await _ensure_acts(db, book_id)
    chapters = (await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order)
    )).scalars().all()
    grouped: dict[uuid.UUID, list[dict[str, Any]]] = {}
    for ch in chapters:
        if ch.act_id:
            grouped.setdefault(ch.act_id, []).append(
                {"id": str(ch.id), "title": ch.title, "number": ch.sort_order,
                 "word_count": ch.word_count or 0}
            )
    return {
        "acts": [
            {
                "id": str(a.id), "title": a.title, "summary": a.summary,
                "sort_order": a.sort_order, "color": a.color, "target_words": a.target_words,
                "chapters": grouped.get(a.id, []),
            }
            for a in acts
        ],
        "unassigned": [
            {"id": str(ch.id), "title": ch.title, "number": ch.sort_order,
             "word_count": ch.word_count or 0}
            for ch in chapters if not ch.act_id
        ],
    }


@router.post("/{project_id}/books/{book_id}/acts", status_code=status.HTTP_201_CREATED)
async def create_act(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: ActIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    existing = await _ensure_acts(db, book_id)
    nxt = max([a.sort_order for a in existing] or [-1]) + 1
    act = Act(book_id=book_id, sort_order=nxt, **payload.model_dump())
    db.add(act)
    await db.commit()
    await db.refresh(act)
    return {"id": str(act.id), "title": act.title, "sort_order": act.sort_order}


@router.patch("/{project_id}/books/{book_id}/acts/{act_id}")
async def update_act(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    act_id: uuid.UUID,
    payload: ActPatch,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    act = await db.get(Act, act_id)
    if not act or act.book_id != book_id:
        raise HTTPException(status_code=404, detail="Act not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(act, key, value)
    await db.commit()
    return {"ok": True}


@router.delete("/{project_id}/books/{book_id}/acts/{act_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_act(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    act_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    act = await db.get(Act, act_id)
    if not act or act.book_id != book_id:
        raise HTTPException(status_code=404, detail="Act not found")
    chapters = (await db.execute(select(Chapter).where(Chapter.act_id == act_id))).scalars().all()
    for ch in chapters:
        ch.act_id = None
    await db.delete(act)
    await db.commit()
    return None


@router.post("/{project_id}/books/{book_id}/acts/reorder")
async def reorder_acts(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: ReorderIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    rows = (await db.execute(select(Act).where(Act.book_id == book_id))).scalars().all()
    by_id = {a.id: a for a in rows}
    for i, act_id in enumerate(payload.order):
        if act_id in by_id:
            by_id[act_id].sort_order = i
    await db.commit()
    return {"ok": True}


@router.patch("/{project_id}/books/{book_id}/chapters/{chapter_id}/act")
async def assign_chapter_act(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
    act_id: uuid.UUID | None = Query(None),
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await db.get(Chapter, chapter_id)
    if not chapter or chapter.book_id != book_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if act_id:
        act = await db.get(Act, act_id)
        if not act or act.book_id != book_id:
            raise HTTPException(status_code=404, detail="Act not found")
    chapter.act_id = act_id
    await db.commit()
    return {"ok": True, "act_id": str(act_id) if act_id else None}


# --------------------------------------------------------------------------- #
# Character relationships within a book - one-way by design
# --------------------------------------------------------------------------- #
class RelationshipIn(BaseModel):
    from_character_id: uuid.UUID
    to_character_id: uuid.UUID
    description: str | None = None
    from_chapter_id: uuid.UUID | None = None


class RelationshipPatch(BaseModel):
    description: str | None = None
    from_chapter_id: uuid.UUID | None = None
    sort_order: int | None = None


class RelationshipOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    from_character_id: uuid.UUID
    from_name: str | None = None
    to_character_id: uuid.UUID
    to_name: str | None = None
    description: str | None = None
    from_chapter_id: uuid.UUID | None = None
    from_chapter_title: str | None = None
    sort_order: int = 0


async def _relationships_payload(db: AsyncSession, book_id: uuid.UUID) -> list[RelationshipOut]:
    rows = (
        await db.execute(
            select(CharacterBond)
            .where(CharacterBond.book_id == book_id)
            .order_by(CharacterBond.sort_order, CharacterBond.created_at)
        )
    ).scalars().all()
    if not rows:
        return []
    ids = {r.from_character_id for r in rows} | {r.to_character_id for r in rows}
    people = (await db.execute(select(Character).where(Character.id.in_(ids)))).scalars().all()
    names = {p.id: p.name for p in people}
    chapters = (
        await db.execute(
            select(Chapter).where(Chapter.id.in_({r.from_chapter_id for r in rows if r.from_chapter_id}))
        )
    ).scalars().all()
    titles = {c.id: c.title for c in chapters}
    return [
        RelationshipOut(
            id=r.id,
            book_id=r.book_id,
            from_character_id=r.from_character_id,
            from_name=names.get(r.from_character_id),
            to_character_id=r.to_character_id,
            to_name=names.get(r.to_character_id),
            description=r.description,
            from_chapter_id=r.from_chapter_id,
            from_chapter_title=titles.get(r.from_chapter_id) if r.from_chapter_id else None,
            sort_order=r.sort_order or 0,
        )
        for r in rows
    ]


@router.get(
    "/{project_id}/books/{book_id}/character-relationships",
    response_model=list[RelationshipOut],
)
async def list_relationships(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    return await _relationships_payload(db, book_id)


@router.post(
    "/{project_id}/books/{book_id}/character-relationships",
    response_model=RelationshipOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: RelationshipIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    if payload.from_character_id == payload.to_character_id:
        raise HTTPException(status_code=422, detail="A character cannot relate to themselves")

    for cid in (payload.from_character_id, payload.to_character_id):
        person = await db.get(Character, cid)
        if person is None or person.project_id != project_id or person.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Character not found")

    existing = (
        await db.execute(
            select(CharacterBond).where(
                CharacterBond.book_id == book_id,
                CharacterBond.from_character_id == payload.from_character_id,
                CharacterBond.to_character_id == payload.to_character_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        if payload.description is not None:
            existing.description = payload.description
        existing.from_chapter_id = payload.from_chapter_id
        await db.commit()
        out = await _relationships_payload(db, book_id)
        return next(r for r in out if r.id == existing.id)

    rel = CharacterBond(
        book_id=book_id,
        from_character_id=payload.from_character_id,
        to_character_id=payload.to_character_id,
        description=payload.description,
        from_chapter_id=payload.from_chapter_id,
    )
    db.add(rel)
    await db.commit()
    await db.refresh(rel)
    out = await _relationships_payload(db, book_id)
    return next(r for r in out if r.id == rel.id)


@router.patch(
    "/{project_id}/books/{book_id}/character-relationships/{relationship_id}",
    response_model=RelationshipOut,
)
async def update_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    relationship_id: uuid.UUID,
    payload: RelationshipPatch,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    rel = await db.get(CharacterBond, relationship_id)
    if rel is None or rel.book_id != book_id:
        raise HTTPException(status_code=404, detail="Relationship not found")
    if payload.description is not None:
        rel.description = payload.description
    if payload.from_chapter_id is not None:
        rel.from_chapter_id = payload.from_chapter_id
    if payload.sort_order is not None:
        rel.sort_order = payload.sort_order
    await db.commit()
    out = await _relationships_payload(db, book_id)
    return next(r for r in out if r.id == rel.id)


@router.delete(
    "/{project_id}/books/{book_id}/character-relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    relationship_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    rel = await db.get(CharacterBond, relationship_id)
    if rel is not None and rel.book_id == book_id:
        await db.delete(rel)
        await db.commit()
    return None


# --------------------------------------------------------------------------- #
# Character portrait - upload only. Generation is not wired to a paid API.
# --------------------------------------------------------------------------- #
PORTRAIT_DIR = "/opt/authora-v2/uploads/portraits"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


@router.post("/{project_id}/characters/{character_id}/portrait", response_model=CharacterOut)
async def upload_portrait(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
    file: Annotated[UploadFile, File()],
):
    await get_project_or_404(db, project_id, current_user.id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id or char.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Character not found")

    ext = ALLOWED_IMAGE_TYPES.get((file.content_type or "").lower())
    if ext is None:
        raise HTTPException(status_code=415, detail="Use a JPEG, PNG, WebP or GIF image")

    blob = await file.read()
    if len(blob) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 8 MB")

    import os
    os.makedirs(PORTRAIT_DIR, exist_ok=True)
    filename = f"{character_id}.{ext}"
    with open(os.path.join(PORTRAIT_DIR, filename), "wb") as handle:
        handle.write(blob)

    char.portrait_url = f"/api/v1/media/portraits/{filename}"
    char.portrait_source = "upload"
    char.portrait_updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(char)
    return _character_out(char)


@router.delete("/{project_id}/characters/{character_id}/portrait", response_model=CharacterOut)
async def delete_portrait(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    char = await db.get(Character, character_id)
    if not char or char.project_id != project_id or char.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Character not found")
    char.portrait_url = None
    char.portrait_source = None
    char.portrait_updated_at = None
    await db.commit()
    await db.refresh(char)
    return _character_out(char)
