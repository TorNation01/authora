"""The repeatable process: nine steps, their real state, and the manuscript review."""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.data.book_bible_schema import SECTIONS as BIBLE_SECTIONS
from authora.data.book_bible_schema import completeness as bible_completeness
from authora.data.book_idea_schema import SECTIONS as IDEA_SECTIONS
from authora.data.book_idea_schema import completeness as idea_completeness
from authora.data.series_bible_schema import completeness as series_completeness
from authora.data.book_process import (
    MANUSCRIPT_QUESTIONS,
    REVIEW_VERDICTS,
    STEPS,
    blank_review,
    normalise_review,
    summarise_review,
)
from authora.database import get_db
from authora.models import (
    Book,
    BookBible,
    BookCharacter,
    BookIdea,
    Chapter,
    ChapterBriefSheet,
    ChapterOutline,
    ManuscriptReview,
    OutlineTurningPoint,
    SeriesBible,
)
from authora.services.ai import complete_sync

logger = logging.getLogger(__name__)

Db = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(prefix="/{project_id}/books/{book_id}", tags=["process"])


def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")


def _walk_text(node: Any, out: list[str]) -> None:
    """Chapter content is ProseMirror JSON - collect every text leaf, whatever the nesting."""
    if isinstance(node, dict):
        text = node.get("text")
        if isinstance(text, str) and text.strip():
            out.append(text)
        for key, value in node.items():
            if key == "text":
                continue
            _walk_text(value, out)
    elif isinstance(node, list):
        for item in node:
            _walk_text(item, out)
    elif isinstance(node, str):
        out.append(node)


def _chapter_text(chapter: Chapter) -> str:
    out: list[str] = []
    _walk_text(chapter.content or {}, out)
    return re.sub(r"\s+", " ", " ".join(_strip_tags(p) for p in out)).strip()


@router.get("/process")
async def get_process(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    book = await get_book_or_404(db, book_id, current_user.id, project_id)

    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()
    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()
    idea_pct = idea_completeness((idea.sections if idea else {}) or {})["pct"]
    series_row = (
        await db.execute(select(SeriesBible).where(SeriesBible.project_id == project_id))
    ).scalar_one_or_none()
    series_stats = series_completeness((series_row.sections if series_row else {}) or {})
    bible_stats = bible_completeness((bible.sections if bible else {}) or {})

    characters = (
        await db.execute(select(func.count()).select_from(BookCharacter).where(BookCharacter.book_id == book_id))
    ).scalar_one()
    points = (
        await db.execute(select(func.count()).select_from(OutlineTurningPoint).where(OutlineTurningPoint.book_id == book_id))
    ).scalar_one()
    chapter_outlines = (
        await db.execute(select(func.count()).select_from(ChapterOutline).where(ChapterOutline.book_id == book_id))
    ).scalar_one()
    briefs = (
        await db.execute(select(func.count()).select_from(ChapterBriefSheet).where(ChapterBriefSheet.book_id == book_id))
    ).scalar_one()
    chapters = (
        await db.execute(
            select(Chapter).where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
        )
    ).scalars().all()
    drafted = [c for c in chapters if (c.word_count or 0) > 0]
    words = sum(c.word_count or 0 for c in chapters)

    last_review = (
        await db.execute(
            select(ManuscriptReview)
            .where(ManuscriptReview.book_id == book_id)
            .order_by(ManuscriptReview.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    def state(done: bool, started: bool) -> str:
        if done:
            return "done"
        return "in_progress" if started else "pending"

    details = {
        "idea": (state(idea_pct >= 60, idea_pct > 0), f"{idea_pct}% of the idea written"),
        "canon": (
            state(series_stats["pct"] >= 60, series_stats["pct"] > 0),
            (
                f"{series_stats['filled']}/{series_stats['total']} canonical facts recorded ({series_stats['pct']}%)"
                if series_stats["filled"]
                else "Series canon: nothing gathered yet"
            ),
        ),
        "characters": (
            state(characters >= 3, characters > 0),
            f"{characters} character{'s' if characters != 1 else ''} attached to this book",
        ),
        "bible": (
            state(bible_stats["pct"] >= 70, bible_stats["pct"] > 0),
            f"{bible_stats['filled']}/{bible_stats['total']} bible fields ({bible_stats['pct']}%)",
        ),
        "outline": (
            state(points >= 8, points > 0),
            f"{points} turning point{'s' if points != 1 else ''}",
        ),
        "chapter_outline": (
            state(chapter_outlines > 0 and chapter_outlines >= len(chapters), chapter_outlines > 0),
            f"{chapter_outlines} chapter outline{'s' if chapter_outlines != 1 else ''}",
        ),
        "briefs": (
            state(briefs > 0 and briefs >= chapter_outlines, briefs > 0),
            f"{briefs} brief{'s' if briefs != 1 else ''} prepared",
        ),
        "write_review": (
            state(len(chapters) > 0 and len(drafted) == len(chapters) and len(drafted) > 0, len(drafted) > 0),
            f"{len(drafted)}/{len(chapters)} chapters drafted · {words:,} words",
        ),
        "manuscript_review": (
            state(last_review is not None, last_review is not None),
            (
                f"Last review {last_review.created_at:%d %b %Y} — {last_review.score}% at {last_review.words_at_review:,} words"
                if last_review
                else "No manuscript review yet"
            ),
        ),
    }

    steps = []
    current_assigned = False
    for step in STEPS:
        step_state, detail = details[step["key"]]
        is_current = False
        if step_state != "done" and not current_assigned:
            is_current = True
            current_assigned = True
        steps.append({**step, "state": step_state, "detail": detail, "current": is_current})

    return {
        "book": {"id": str(book.id), "title": book.title},
        "steps": steps,
        "current": next((s["key"] for s in steps if s["current"]), None),
        "totals": {
            "chapters": len(chapters),
            "drafted": len(drafted),
            "words": words,
            "characters": characters,
            "turning_points": points,
        },
    }


def _review_payload(run: ManuscriptReview | None, totals: dict[str, Any] | None = None) -> dict[str, Any]:
    if run is None:
        return {
            "run": None,
            "questions": MANUSCRIPT_QUESTIONS,
            "answers": blank_review(),
            "summary": summarise_review({}),
            "totals": totals or {},
        }
    answers = normalise_review(run.answers or {})
    return {
        "run": {
            "id": str(run.id),
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "score": run.score,
            "words": run.words_at_review,
            "chapters": run.chapters_at_review,
            "model": run.model,
        },
        "questions": MANUSCRIPT_QUESTIONS,
        "answers": answers,
        "summary": summarise_review(answers),
        "totals": totals or {},
    }


@router.get("/process/review")
async def get_manuscript_review(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Db,
):
    await get_book_or_404(db, book_id, current_user.id, project_id)
    run = (
        await db.execute(
            select(ManuscriptReview)
            .where(ManuscriptReview.book_id == book_id)
            .order_by(ManuscriptReview.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return _review_payload(run)


def _parse_review_json(raw: str | None) -> dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        return {}
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)
        text = re.sub(r"```\s*$", "", text).strip()
    candidates = [text]
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
                out = {str(i["key"]): i for i in answers if isinstance(i, dict) and i.get("key")}
                if out:
                    return out
    salvaged: dict[str, Any] = {}
    for match in re.finditer(r'\{[^{}]*?"key"\s*:\s*"([a-z_]+)"[^{}]*?\}', text):
        try:
            item = json.loads(re.sub(r",\s*([}\]])", r"\1", match.group()))
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(item, dict) and item.get("key"):
            salvaged[str(item["key"])] = item
    return salvaged


@router.post("/process/review/run")
async def run_manuscript_review(
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
            .order_by(Chapter.sort_order, Chapter.created_at)
        )
    ).scalars().all()
    drafted = [c for c in chapters if (c.word_count or 0) > 0]
    if not drafted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no drafted prose to review yet. Write a chapter first.",
        )

    idea = (await db.execute(select(BookIdea).where(BookIdea.book_id == book_id))).scalar_one_or_none()
    bible = (await db.execute(select(BookBible).where(BookBible.book_id == book_id))).scalar_one_or_none()

    promise = ""
    if idea:
        sections = idea.sections or {}
        for key in ("premise", "hook_and_promise", "emotional_core", "ending_and_direction"):
            block = sections.get(key) or {}
            for field_key, value in block.items():
                if isinstance(value, str) and value.strip():
                    promise += f"- {field_key}: {value.strip()[:600]}\n"
    bible_facts = ""
    if bible:
        sections = bible.sections or {}
        for key in ("world", "continuity", "characters", "tone"):
            block = sections.get(key) or {}
            for field_key, value in block.items():
                if isinstance(value, str) and value.strip():
                    bible_facts += f"- {field_key}: {value.strip()[:400]}\n"

    chunks: list[str] = []
    budget = 32000
    for chapter in drafted:
        text = _chapter_text(chapter)
        excerpt = text if len(text) <= 2600 else f"{text[:1700]} … {text[-800:]}"
        block = f"\n### {chapter.sort_order + 1}. {chapter.title} ({chapter.word_count:,} words)\n{excerpt}\n"
        if sum(len(c) for c in chunks) + len(block) > budget:
            chunks.append(f"\n### {chapter.title} ({chapter.word_count:,} words)\n(excerpt omitted for length)\n")
        else:
            chunks.append(block)
    manuscript = "".join(chunks)

    question_list = "\n".join(
        f"{i + 1}. [{q['key']}] {q['label']} Look for: {q['look_for']}"
        for i, q in enumerate(MANUSCRIPT_QUESTIONS)
    )

    prompt = f"""You are reviewing a complete novel manuscript. Be exacting; do not flatter.

BOOK: {book.title}
CHAPTERS DRAFTED: {len(drafted)} of {len(chapters)} · {sum(c.word_count or 0 for c in chapters):,} words

THE PROMISE THE BOOK MAKES:
{promise or "(the idea has not been written yet)"}

ESTABLISHED CANON:
{bible_facts or "(no bible written yet)"}

THE DRAFT:
{manuscript}

Answer all nine questions:
{question_list}

Rules:
- verdict is one of: pass, partial, fail, unknown. Use unknown only when the draft gives no evidence.
- evidence must quote or closely paraphrase a specific moment from the draft, naming the chapter. Never invent.
- note is at most 25 words: what to fix, or the strongest evidence if it passes.
- Remember the goal: a complete novel at the depth it needs, not padded and not compressed to plot only.

Return JSON only:
{{"answers": [{{"key": "promise_fulfilled", "verdict": "partial", "note": "...", "evidence": "..."}}, ...]}}"""

    system = (
        "You are a structural and line editor assessing a finished draft. You judge promise, character, "
        "world, depth, scene life, repetition, earned endings and series consistency. You never invent quotes."
    )

    try:
        raw = await complete_sync(prompt, system, max_tokens=4000)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"The manuscript review could not run: {exc}") from exc

    parsed = _parse_review_json(raw)
    if not parsed:
        logger.warning("manuscript review: unparseable response: %r", (raw or "")[:500])
        try:
            raw = await complete_sync(prompt + "\n\nReturn only the JSON object. No prose, no code fences.", system, max_tokens=4000)
        except Exception:  # noqa: BLE001
            raw = ""
        parsed = _parse_review_json(raw)

    answers = normalise_review(parsed)
    summary = summarise_review(answers)
    words = sum(c.word_count or 0 for c in chapters)
    run = ManuscriptReview(
        book_id=book_id,
        answers=answers,
        counts=summary["counts"],
        score=summary["pct"],
        words_at_review=words,
        chapters_at_review=len(drafted),
        model="authora-ai",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return _review_payload(run, {"chapters": len(chapters), "drafted": len(drafted), "words": words})
