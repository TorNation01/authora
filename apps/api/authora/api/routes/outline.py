"""Overall Outline - the turning-point builder."""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.data.book_bible_schema import SECTIONS as BIBLE_SECTIONS
from authora.data.book_idea_schema import SECTIONS as IDEA_SECTIONS
from authora.data.act_brief_schema import SECTION_BY_KEY as ACT_SECTION_BY_KEY
from authora.data.act_brief_schema import act_section as resolve_act_section
from authora.data.outline_check_schema import QUESTIONS as CHECK_QUESTIONS
from authora.data.outline_check_schema import blank_answers as check_blank_answers
from authora.data.outline_check_schema import normalise as check_normalise
from authora.data.outline_check_schema import summarise as check_summarise
from authora.data.act_brief_schema import normalise as act_normalise
from authora.data.outline_schema import FIELDS, FIELD_BY_KEY, blank_fields, filled_count, normalise
from authora.database import get_db
from authora.models import Act, BookBible, BookIdea, OutlineActSheet, OutlineCheckRun, OutlineTurningPoint
from authora.services.ai import complete_sync

router = APIRouter(prefix="/projects", tags=["outline"])

Db = Annotated[AsyncSession, Depends(get_db)]


async def _owned_tp(db: AsyncSession, tp_id: uuid.UUID, book_id: uuid.UUID) -> OutlineTurningPoint:
    tp = await db.get(OutlineTurningPoint, tp_id)
    if tp is None or tp.book_id != book_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turning point not found")
    return tp


def _tp_payload(tp: OutlineTurningPoint) -> dict[str, Any]:
    body = normalise(tp.fields)
    return {
        "id": str(tp.id),
        "book_id": str(tp.book_id),
        "act_id": str(tp.act_id) if tp.act_id else None,
        "sort_order": tp.sort_order,
        "title": tp.title,
        "fields": body,
        "filled": filled_count(body),
        "total": len(FIELDS),
        "version": tp.version,
    }


class TurningPointIn(BaseModel):
    title: str = ""
    act_id: uuid.UUID | None = None
    fields: dict[str, Any] = Field(default_factory=dict)
    after_id: uuid.UUID | None = None


class TurningPointPatch(BaseModel):
    title: str | None = None
    act_id: uuid.UUID | None = None
    fields: dict[str, Any] | None = None
    clear_act: bool = False


class MoveRequest(BaseModel):
    direction: str


class DraftRequest(BaseModel):
    field: str


class DraftResponse(BaseModel):
    text: str


@router.get("/book-outline/schema")
async def outline_schema():
    return {"fields": FIELDS}


@router.get("/{project_id}/books/{book_id}/outline")
async def list_outline(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order, OutlineTurningPoint.created_at)
        )
    ).scalars().all()
    acts = (
        await db.execute(select(Act).where(Act.book_id == book_id).order_by(Act.sort_order))
    ).scalars().all()

    total = len(points) * len(FIELDS)
    filled = sum(filled_count(p.fields) for p in points)
    return {
        "book_id": str(book.id),
        "book_title": book.title,
        "turning_points": [_tp_payload(p) for p in points],
        "acts": [{"id": str(a.id), "title": a.title, "sort_order": a.sort_order} for a in acts],
        "progress": {
            "filled": filled,
            "total": total,
            "pct": round(filled / total * 100) if total else 0,
            "points": len(points),
        },
    }


@router.post("/{project_id}/books/{book_id}/outline", status_code=status.HTTP_201_CREATED)
async def create_turning_point(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: TurningPointIn,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)

    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order)
        )
    ).scalars().all()

    if payload.after_id is not None:
        anchor = next((p for p in points if p.id == payload.after_id), None)
        insert_at = (anchor.sort_order + 1) if anchor else len(points)
        for point in points:
            if point.sort_order >= insert_at:
                point.sort_order += 1
    else:
        insert_at = len(points)

    tp = OutlineTurningPoint(
        book_id=book_id,
        act_id=payload.act_id,
        sort_order=insert_at,
        title=payload.title or f"Turning point {len(points) + 1}",
        fields=normalise(payload.fields),
        version=1,
    )
    db.add(tp)
    await db.commit()
    await db.refresh(tp)
    return _tp_payload(tp)


@router.patch("/{project_id}/books/{book_id}/outline/{tp_id}")
async def patch_turning_point(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tp_id: uuid.UUID,
    payload: TurningPointPatch,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    tp = await _owned_tp(db, tp_id, book_id)

    if payload.title is not None:
        tp.title = payload.title
    if payload.clear_act:
        tp.act_id = None
    elif payload.act_id is not None:
        tp.act_id = payload.act_id
    if payload.fields is not None:
        merged = normalise(tp.fields)
        for key, value in payload.fields.items():
            if key in FIELD_BY_KEY:
                merged[key] = value
        tp.fields = merged
    tp.version = (tp.version or 1) + 1

    await db.commit()
    await db.refresh(tp)
    return _tp_payload(tp)


@router.delete("/{project_id}/books/{book_id}/outline/{tp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_turning_point(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tp_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    tp = await _owned_tp(db, tp_id, book_id)
    await db.delete(tp)
    await db.commit()
    return None


@router.post("/{project_id}/books/{book_id}/outline/{tp_id}/move")
async def move_turning_point(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tp_id: uuid.UUID,
    payload: MoveRequest,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    tp = await _owned_tp(db, tp_id, book_id)

    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order)
        )
    ).scalars().all()
    index = next((i for i, p in enumerate(points) if p.id == tp.id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Turning point not found")

    target = index - 1 if payload.direction == "up" else index + 1
    if target < 0 or target >= len(points):
        return {"moved": False}

    points[index], points[target] = points[target], points[index]
    for position, point in enumerate(points):
        point.sort_order = position
    await db.commit()
    return {"moved": True}


def _render_sections(sections: dict[str, Any], schema: list[dict[str, Any]], limit: int) -> str:
    lines: list[str] = []
    for section in schema:
        body = (sections or {}).get(section["key"]) or {}
        rendered: list[str] = []
        for field in section["fields"]:
            value = body.get(field["key"])
            if isinstance(value, list):
                rows = [str(v) for v in value if str(v or "").strip()]
                if rows:
                    rendered.append(f"- {field['label']}: " + "; ".join(rows))
            elif str(value or "").strip():
                rendered.append(f"- {field['label']}: {value}")
        if rendered:
            lines.append(f"{section['title']}:\n" + "\n".join(rendered))
    return "\n\n".join(lines)[:limit]


@router.post("/{project_id}/books/{book_id}/outline/{tp_id}/draft-field", response_model=DraftResponse)
async def draft_turning_point_field(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tp_id: uuid.UUID,
    payload: DraftRequest,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    tp = await _owned_tp(db, tp_id, book_id)

    field = FIELD_BY_KEY.get(payload.field)
    if field is None:
        raise HTTPException(status_code=400, detail="Unknown field")
    if not field.get("ai"):
        raise HTTPException(status_code=400, detail="That field is not drafted - it is yours to decide")

    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()

    all_points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order)
        )
    ).scalars().all()
    index = next((i for i, p in enumerate(all_points) if p.id == tp.id), 0)

    def summarise(point: OutlineTurningPoint) -> str:
        body = normalise(point.fields)
        bits = [f"{point.sort_order + 1}. {point.title or '(untitled)'}"]
        for key in ("what_happens", "consequence", "chapter_range"):
            value = body.get(key)
            if str(value or "").strip():
                bits.append(f"   {FIELD_BY_KEY[key]['label']}: {value}")
        return "\n".join(bits)

    before = [p for p in all_points[:index] if p.id != tp.id]
    after = [p for p in all_points[index + 1 :] if p.id != tp.id]
    neighbours = "\n".join([summarise(p) for p in before[-2:]] + [summarise(p) for p in after[:2]])

    current_body = normalise(tp.fields)
    current_text = "\n".join(
        f"- {FIELD_BY_KEY[k]['label']}: {v}"
        for k, v in current_body.items()
        if k in FIELD_BY_KEY and str(v or "").strip() and k != payload.field
    )

    idea_text = _render_sections(idea.sections if idea else {}, IDEA_SECTIONS, 6000)
    bible_text = _render_sections(bible.sections if bible else {}, BIBLE_SECTIONS, 9000)

    shape = (
        "Reply with the points only, one per line, each starting with '- '."
        if field["type"] == "list"
        else "Reply with the answer only: no preamble, no headings, no quotation marks."
    )

    prompt = f"""You are helping an author build the overall outline of a novel, one turning point at a time.

BOOK: {book.title}

THE BOOK IDEA (what this book is for):
{idea_text or "(not written yet)"}

THE BOOK BIBLE (established facts - never contradict these):
{bible_text or "(not written yet)"}

WHERE THIS TURNING POINT SITS: position {index + 1} of {len(all_points)}. Title: {tp.title or "(untitled)"}

NEIGHBOURING TURNING POINTS:
{neighbours or "(none yet)"}

WHAT IS ALREADY WRITTEN ON THIS TURNING POINT:
{current_text or "(nothing yet)"}

Answer this one question for this turning point:
{field['label']} - {field['prompt']}

Stay inside the established facts. Do not invent proper nouns, places or characters that are not already in the material. If the material does not support a specific answer, make a concrete proposal and mark it explicitly as a proposal. Keep it to what this section can actually bear. {shape}"""
    system = (
        "You are a structural story editor. You think in cause and effect, you refuse filler, "
        "and you never invent facts about the author's book."
    )

    try:
        text = await complete_sync(prompt, system, max_tokens=600)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"AI drafting unavailable: {exc}") from exc

    return DraftResponse(text=(text or "").strip())


# ---------------------------------------------------------------------------
# Act sheets - what each major section must establish (layer three, part two)
# ---------------------------------------------------------------------------


class ActValues(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)
    title: str | None = None


class NewAct(BaseModel):
    title: str | None = None


async def _act_sheet(db: AsyncSession, book_id: uuid.UUID, act_key: str) -> OutlineActSheet | None:
    return (
        await db.execute(
            select(OutlineActSheet).where(
                OutlineActSheet.book_id == book_id, OutlineActSheet.act_key == act_key
            )
        )
    ).scalar_one_or_none()


def _act_payload(act_key: str, sheet: OutlineActSheet | None) -> dict[str, Any]:
    section = resolve_act_section(
        act_key,
        sheet.title if sheet and sheet.title else None,
        sheet.position if sheet and sheet.position is not None else None,
    )
    body = act_normalise({act_key: (sheet.sections or {}).get(act_key, {}) if sheet else {}})[act_key]
    return {
        "key": act_key,
        "number": section["number"],
        "title": section["title"],
        "intro": section["intro"],
        "fields": section["fields"],
        "values": body,
        "filled": sum(1 for v in body.values() if str(v).strip()),
        "total": len(section["fields"]),
        "version": sheet.version if sheet else 0,
    }


@router.get("/{project_id}/books/{book_id}/outline/acts")
async def list_act_sheets(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    rows = (
        await db.execute(select(OutlineActSheet).where(OutlineActSheet.book_id == book_id))
    ).scalars().all()
    sheets = {s.act_key: s for s in rows}
    # The first three acts always exist; anything else the author added follows in their order.
    extra = sorted(
        (r for r in rows if r.act_key not in ACT_SECTION_BY_KEY),
        key=lambda r: (r.position if r.position is not None else 999, r.created_at or r.id),
    )
    keys = list(ACT_SECTION_BY_KEY) + [r.act_key for r in extra]
    sections = [_act_payload(key, sheets.get(key)) for key in keys]
    filled = sum(s["filled"] for s in sections)
    total = sum(s["total"] for s in sections)
    return {
        "book_id": str(book.id),
        "book_title": book.title,
        "sections": sections,
        "progress": {
            "filled": filled,
            "total": total,
            "pct": round(filled / total * 100) if total else 0,
        },
    }


@router.patch("/{project_id}/books/{book_id}/outline/acts/{act_key}")
async def patch_act_sheet(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    act_key: str,
    payload: ActValues,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    known = act_key in ACT_SECTION_BY_KEY or (act_key.startswith("act_") and act_key[4:].isdigit())
    if not known:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown act section")

    sheet = await _act_sheet(db, book_id, act_key)
    if sheet is None:
        if act_key not in ACT_SECTION_BY_KEY:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="That act does not exist yet")
        sheet = OutlineActSheet(book_id=book_id, act_key=act_key, sections={}, version=1)
        db.add(sheet)
        await db.flush()

    section = resolve_act_section(
        act_key,
        sheet.title if sheet.title else None,
        sheet.position if sheet.position is not None else None,
    )
    if payload.title is not None and payload.title.strip():
        sheet.title = payload.title.strip()[:120]
        section = resolve_act_section(act_key, sheet.title, sheet.position)
    # Keep every act's stored body addressable even when a new act has never been written to.
    current = act_normalise({**act_normalise(sheet.sections or {}), act_key: (sheet.sections or {}).get(act_key, {})})
    allowed = {f["key"] for f in section["fields"]}
    for key, value in (payload.values or {}).items():
        if key in allowed:
            current.setdefault(act_key, {})[key] = str(value or "")
    sheet.sections = current
    sheet.version = (sheet.version or 1) + 1
    await db.commit()
    await db.refresh(sheet)
    return _act_payload(act_key, sheet)


@router.post("/{project_id}/books/{book_id}/outline/acts")
async def create_act_sheet(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    payload: NewAct,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    rows = (
        await db.execute(select(OutlineActSheet).where(OutlineActSheet.book_id == book_id))
    ).scalars().all()
    numbers = []
    for row in rows:
        if row.act_key.startswith("act_") and row.act_key[4:].isdigit():
            numbers.append(int(row.act_key[4:]))
        if row.position:
            numbers.append(row.position)
    number = max(numbers + [3]) + 1
    act_key = f"act_{number}"
    title = (payload.title or "").strip() or f"Act {number}"
    sheet = OutlineActSheet(
        book_id=book_id, act_key=act_key, title=title[:120], position=number, sections={}, version=1
    )
    db.add(sheet)
    await db.commit()
    await db.refresh(sheet)
    return _act_payload(act_key, sheet)


@router.delete("/{project_id}/books/{book_id}/outline/acts/{act_key}")
async def delete_act_sheet(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    act_key: str,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    if act_key in ACT_SECTION_BY_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The first three acts are structural. Rename them instead of deleting them.",
        )
    sheet = await _act_sheet(db, book_id, act_key)
    if sheet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="That act does not exist")
    await db.delete(sheet)
    await db.commit()
    return {"deleted": act_key}


@router.post(
    "/{project_id}/books/{book_id}/outline/acts/{act_key}/draft-field",
    response_model=DraftResponse,
)
async def draft_act_field(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    act_key: str,
    payload: DraftRequest,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    if not (act_key in ACT_SECTION_BY_KEY or (act_key.startswith("act_") and act_key[4:].isdigit())):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown act section")
    sheet_row = await _act_sheet(db, book_id, act_key)
    section = resolve_act_section(
        act_key,
        sheet_row.title if sheet_row and sheet_row.title else None,
        sheet_row.position if sheet_row and sheet_row.position is not None else None,
    )
    field = next((f for f in section["fields"] if f["key"] == payload.field), None)
    if field is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown field")

    sheet = await _act_sheet(db, book_id, act_key)
    body = act_normalise({act_key: (sheet.sections or {}).get(act_key, {}) if sheet else {}})[act_key]

    idea = (
        await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))
    ).scalar_one_or_none()
    bible = (
        await db.execute(select(BookBible).where(BookBible.book_id == book_id))
    ).scalar_one_or_none()
    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order, OutlineTurningPoint.created_at)
        )
    ).scalars().all()

    idea_text = _render_sections(idea.sections if idea else {}, IDEA_SECTIONS, 6000)
    bible_text = _render_sections(bible.sections if bible else {}, BIBLE_SECTIONS, 9000)
    locked = [
        s["title"]
        for s in BIBLE_SECTIONS
        if (getattr(bible, "section_status", None) or {}).get(s["key"]) == "locked"
    ] if bible else []
    outline_text = "\n".join(
        f"{i + 1}. {p.title or '(untitled)'}" for i, p in enumerate(points)
    )
    written = "\n".join(f"- {f['label']}: {v}" for f, v in ((f, body.get(f["key"])) for f in section["fields"]) if str(v).strip())

    prompt = f"""You are helping an author plan the {section['title'].lower()} of a novel.

BOOK: {book.title}

THE BOOK IDEA (what this book is for):
{idea_text or "(not written yet)"}

THE BOOK BIBLE (established facts - never contradict these):
{bible_text or "(not written yet)"}

LOCKED CANON - sealed decisions, do not revise or contradict: {', '.join(locked) if locked else '(none marked locked yet)'}

THE TURNING POINTS SO FAR:
{outline_text or "(none yet)"}

ALREADY WRITTEN FOR THIS SECTION:
{written or "(nothing yet)"}

Answer this one question for this section:
{field['label']} - {field['prompt']}

Reply with the answer only: no preamble, no headings, no quotation marks. Two to five sentences. Stay inside the established facts and do not invent proper nouns. If the material does not support a specific answer, make a concrete proposal and mark it as a proposal."""

    system = (
        "You are a structural story editor. You think in cause and effect, you refuse filler, "
        "and you never invent facts about the author's book."
    )
    try:
        text = await complete_sync(prompt, system, max_tokens=500)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"AI drafting unavailable: {exc}") from exc
    return DraftResponse(text=(text or "").strip())


def _parse_check_json(raw: str | None) -> dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        return {}
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)
        text = re.sub(r"```\s*$", "", text).strip()
    candidates: list[str] = [text]
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidates.append(match.group())
    for candidate in candidates:
        for attempt in (candidate, re.sub(r",\s*([}\]])", r"\1", candidate)):
            try:
                payload = json.loads(attempt)
            except (json.JSONDecodeError, ValueError):
                continue
            answers = payload.get("answers")
            if isinstance(answers, dict):
                answers = [{"key": k, **(v if isinstance(v, dict) else {"note": str(v)})} for k, v in answers.items()]
            if isinstance(answers, list):
                out = {
                    str(item["key"]): item
                    for item in answers
                    if isinstance(item, dict) and item.get("key")
                }
                if out:
                    return out

    # Last resort: salvage complete per-question objects from a truncated payload.
    salvaged: dict[str, Any] = {}
    for match in re.finditer(r'\{[^{}]*?"key"\s*:\s*"([a-z_]+)"[^{}]*?\}', text):
        try:
            item = json.loads(re.sub(r",\s*([}\]])", r"\1", match.group()))
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(item, dict) and item.get("key"):
            salvaged[str(item["key"])] = item
    return salvaged


# ---------------------------------------------------------------------------
# The twelve-question outline check
# ---------------------------------------------------------------------------


def _check_payload(run: OutlineCheckRun | None) -> dict[str, Any]:
    if run is None:
        return {
            "run": None,
            "questions": CHECK_QUESTIONS,
            "answers": check_blank_answers(),
            "summary": check_summarise({}),
        }
    answers = check_normalise(run.answers or {})
    return {
        "run": {
            "id": str(run.id),
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "score": run.score,
            "model": run.model,
        },
        "questions": CHECK_QUESTIONS,
        "answers": answers,
        "summary": check_summarise(answers),
    }


@router.get("/{project_id}/books/{book_id}/outline/check")
async def get_outline_check(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    run = (
        await db.execute(
            select(OutlineCheckRun)
            .where(OutlineCheckRun.book_id == book_id)
            .order_by(OutlineCheckRun.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return _check_payload(run)


@router.post("/{project_id}/books/{book_id}/outline/check/run")
async def run_outline_check(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)

    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()
    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    points = (
        await db.execute(
            select(OutlineTurningPoint)
            .where(OutlineTurningPoint.book_id == book_id)
            .order_by(OutlineTurningPoint.sort_order, OutlineTurningPoint.created_at)
        )
    ).scalars().all()
    sheets = (
        await db.execute(select(OutlineActSheet).where(OutlineActSheet.book_id == book_id))
    ).scalars().all()

    if not points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is nothing to check yet - add turning points first.",
        )

    idea_text = _render_sections(idea.sections if idea else {}, IDEA_SECTIONS, 5000)
    bible_text = _render_sections(bible.sections if bible else {}, BIBLE_SECTIONS, 7000)

    outline_lines: list[str] = []
    for index, point in enumerate(points, start=1):
        body = normalise({f["key"]: (point.fields or {}).get(f["key"], "") for f in FIELDS})  # type: ignore[arg-type]
        outline_lines.append(f"\n{index}. {point.title or '(untitled)'}")
        for field in FIELDS:
            value = body.get(field["key"])
            if isinstance(value, list):
                value = "; ".join(str(v) for v in value if str(v).strip())
            if str(value or "").strip():
                outline_lines.append(f"   - {field['label']}: {value}")
    outline_text = "\n".join(outline_lines)

    act_by_key = {s.act_key: s for s in sheets}
    act_text_parts: list[str] = []
    for key, section in ACT_SECTION_BY_KEY.items():
        sheet = act_by_key.get(key)
        body = act_normalise({key: (sheet.sections or {}).get(key, {}) if sheet else {}})[key]
        lines = [f"{section['title']}:"]
        for field in section["fields"]:
            value = str(body.get(field["key"], "") or "").strip()
            if value:
                lines.append(f"  - {field['label']}: {value}")
        if len(lines) > 1:
            act_text_parts.append("\n".join(lines))
    act_text = "\n\n".join(act_text_parts)

    question_list = "\n".join(f"{i + 1}. [{q['key']}] {q['label']} Look for: {q['look_for']}" for i, q in enumerate(CHECK_QUESTIONS))

    prompt = f"""You are auditing a novel outline before it is drafted. Be exacting. Praise nothing.

BOOK: {book.title}

THE BOOK IDEA (the promise the book makes):
{idea_text or "(not written yet)"}

THE BOOK BIBLE (established facts):
{bible_text or "(not written yet)"}

SECTION SHEETS (what each act must establish):
{act_text or "(none written yet)"}

THE TURNING POINTS:
{outline_text}

Answer all twelve questions:
{question_list}

Rules:
- verdict is one of: pass, partial, fail, unknown.
- Use "unknown" only when the outline genuinely contains no evidence either way.
- evidence must quote or closely paraphrase a specific title, line or section from the material above. Never invent a scene that is not there.
- note is at most 25 words: what to fix.
- evidence is at most 20 words, quoting the material. If the verdict is pass, name the strongest piece of evidence instead.
- A thin outline must fail on the questions that depend on missing material; do not award credit for good intentions.

Return JSON only, in this shape:
{{"answers": [{{"key": "causality", "verdict": "partial", "note": "...", "evidence": "..."}}, ...]}}"""

    system = (
        "You are a structural story editor auditing an outline. You judge cause, agency, stakes, "
        "relationship movement, world texture, consequence and delivery of the promise. You do not flatter."
    )

    try:
        raw = await complete_sync(prompt, system, max_tokens=4000)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"The outline check could not run: {exc}") from exc

    parsed = _parse_check_json(raw)
    if not parsed:
        logger.warning("outline check: unparseable response: %r", (raw or "")[:500])
        try:
            raw = await complete_sync(
                prompt + "\n\nReturn only the JSON object. No prose, no code fences.",
                system,
                max_tokens=3000,
            )
        except Exception:  # noqa: BLE001
            raw = ""
        parsed = _parse_check_json(raw)
        if not parsed:
            logger.warning("outline check: retry also unparseable: %r", (raw or "")[:500])

    answers = check_normalise(parsed)
    summary = check_summarise(answers)
    run = OutlineCheckRun(
        book_id=book_id,
        answers=answers,
        counts=summary["counts"],
        score=summary["pct"],
        material="outline",
        model="authora-ai",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return _check_payload(run)
