"""Editing engine orchestration: run analysis jobs, produce reports."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, EditorialAnalysis, EditorialJob, EditorialSuggestion
from authora.services.editing.text_utils import tiptap_to_plain_text
from authora.services.editing.readability import analyze_readability
from authora.services.editing.patterns import (
    detect_filler_words,
    detect_passive_voice,
    detect_repeated_phrases,
    analyze_sentence_length,
)
from authora.services.editing.ai_analysis import (
    analyze_grammar_clarity,
    analyze_structure,
    analyze_fiction_hints,
    analyze_nonfiction_hints,
)


async def run_chapter_analysis(
    db: AsyncSession,
    chapter_id: UUID,
    book_id: UUID,
    user_id: UUID,
    *,
    include_ai: bool = True,
) -> EditorialJob:
    """Run full analysis on a single chapter."""
    job = EditorialJob(
        book_id=book_id,
        user_id=user_id,
        scope="chapter",
        chapter_id=chapter_id,
        status="running",
    )
    db.add(job)
    await db.flush()

    try:
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
        chapter = result.scalar_one_or_none()
        if not chapter:
            job.status = "failed"
            job.error_message = "Chapter not found"
            await db.flush()
            return job

        book_result = await db.execute(select(Book).where(Book.id == book_id))
        book = book_result.scalar_one_or_none()
        text = tiptap_to_plain_text(chapter.content)
        book_type = book.type if book else "fiction"

        # Run all analyses
        analyses = []

        # 1. Readability
        readability = analyze_readability(text)
        analyses.append(("readability", readability))

        # 2. Sentence length
        sent_balance = analyze_sentence_length(text)
        analyses.append(("sentence_balance", sent_balance))

        # 3. Filler words
        filler = detect_filler_words(text)
        analyses.append(("filler_words", {"items": filler}))

        # 4. Passive voice
        passive = detect_passive_voice(text)
        analyses.append(("passive_voice", {"items": passive}))

        # 5. Repeated phrases
        repeated = detect_repeated_phrases(text)
        analyses.append(("repeated_phrases", {"items": repeated}))

        # 6. AI: grammar/clarity
        if include_ai:
            grammar = await analyze_grammar_clarity(text, book_type)
            analyses.append(("grammar_clarity", grammar))

            # 7. AI: structure
            structure = await analyze_structure(text, chapter.title)
            analyses.append(("structure", structure))

            # 8. Fiction or nonfiction hints
            if book_type == "fiction":
                fiction_hints = await analyze_fiction_hints(text)
                analyses.append(("fiction_hints", fiction_hints))
            else:
                nf_hints = await analyze_nonfiction_hints(text)
                analyses.append(("nonfiction_hints", nf_hints))

        # Persist analyses
        for analysis_type, result_data in analyses:
            analysis = EditorialAnalysis(
                chapter_id=chapter_id,
                job_id=job.id,
                analysis_type=analysis_type,
                result=result_data,
            )
            db.add(analysis)
            await db.flush()

            # Create inline suggestions from grammar issues
            if analysis_type == "grammar_clarity" and isinstance(result_data, dict):
                issues = result_data.get("issues", [])
                for issue in issues[:10]:
                    sugg = EditorialSuggestion(
                        chapter_id=chapter_id,
                        analysis_id=analysis.id,
                        suggestion_type=issue.get("type", "grammar"),
                        original_text=issue.get("original"),
                        suggested_text=issue.get("suggestion"),
                        suggestion_metadata={"severity": issue.get("severity", "medium")},
                        status="pending",
                    )
                    db.add(sugg)

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)[:500]
    await db.flush()
    return job


async def run_book_analysis(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    *,
    include_ai: bool = True,
) -> list[EditorialJob]:
    """Run analysis on all chapters of a book."""
    result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order)
    )
    chapters = list(result.scalars().all())
    jobs = []
    for ch in chapters:
        job = await run_chapter_analysis(db, ch.id, book_id, user_id, include_ai=include_ai)
        jobs.append(job)
    return jobs


def build_chapter_scorecard(analyses: list[EditorialAnalysis]) -> dict:
    """Build a chapter scorecard from analyses."""
    by_type = {a.analysis_type: a.result for a in analyses}
    scorecard = {
        "readability": by_type.get("readability", {}),
        "sentence_balance": by_type.get("sentence_balance", {}),
        "filler_words": by_type.get("filler_words", {}),
        "passive_voice": by_type.get("passive_voice", {}),
        "repeated_phrases": by_type.get("repeated_phrases", {}),
        "grammar_clarity": by_type.get("grammar_clarity", {}),
        "structure": by_type.get("structure", {}),
        "fiction_hints": by_type.get("fiction_hints", {}),
        "nonfiction_hints": by_type.get("nonfiction_hints", {}),
    }
    # Overall health score (0-100)
    scores = []
    if "flesch_reading_ease" in scorecard.get("readability", {}):
        r = scorecard["readability"]["flesch_reading_ease"]
        scores.append(min(100, max(0, r)))
    if "balance_score" in scorecard.get("sentence_balance", {}):
        scores.append(scorecard["sentence_balance"]["balance_score"])
    if "clarity_score" in scorecard.get("grammar_clarity", {}):
        scores.append(scorecard["grammar_clarity"]["clarity_score"])
    if "opening_strength" in scorecard.get("structure", {}):
        scores.append(scorecard["structure"]["opening_strength"])
    if "ending_strength" in scorecard.get("structure", {}):
        scores.append(scorecard["structure"]["ending_strength"])
    scorecard["overall_score"] = round(sum(scores) / len(scores), 1) if scores else 0
    return scorecard


def build_manuscript_health(chapters_data: list[dict]) -> dict:
    """Build manuscript-level health dashboard from chapter scorecards."""
    if not chapters_data:
        return {"overall_score": 0, "chapters": [], "summary": "No chapters analyzed."}
    scores = [c.get("overall_score", 0) for c in chapters_data if isinstance(c, dict)]
    avg = sum(scores) / len(scores) if scores else 0
    return {
        "overall_score": round(avg, 1),
        "chapter_count": len(chapters_data),
        "chapters": chapters_data,
        "summary": f"Average score: {round(avg, 1)}/100 across {len(chapters_data)} chapters.",
    }
