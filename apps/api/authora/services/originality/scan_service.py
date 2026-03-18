"""Originality scan orchestration service."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, ComparisonCorpus, MatchedPassage, OriginalityScan
from authora.services.originality import (
    compare_against_corpus,
    compute_overall_similarity,
    extract_plain_text_from_chapters,
)


def _chapter_to_dict(ch: Chapter) -> dict[str, Any]:
    """Convert Chapter model to dict for similarity engine."""
    return {
        "id": str(ch.id),
        "content": ch.content or {},
        "title": ch.title or "",
        "sort_order": ch.sort_order or 0,
    }


async def run_originality_scan(
    db: AsyncSession,
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    created_by: uuid.UUID | None,
    *,
    corpus_ids: list[uuid.UUID] | None = None,
    excluded_ranges: list[dict[str, Any]] | None = None,
    min_similarity: float = 0.5,
) -> OriginalityScan:
    """
    Run originality/similarity scan. Results are review aids only.
    Does not claim perfect plagiarism detection.
    """
    scan = OriginalityScan(
        project_id=project_id,
        book_id=book_id,
        status="running",
        excluded_ranges=excluded_ranges,
        corpus_ids=[str(c) for c in corpus_ids] if corpus_ids else None,
        created_by=created_by,
    )
    db.add(scan)
    await db.flush()

    try:
        # Load book chapters
        result = await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
            .order_by(Chapter.sort_order)
        )
        chapters = list(result.scalars().all())
        query_chapters = extract_plain_text_from_chapters([_chapter_to_dict(c) for c in chapters])

        if not query_chapters:
            scan.status = "completed"
            scan.overall_similarity_pct = 0.0
            scan.completed_at = datetime.now(timezone.utc)
            return scan

        corpus_chapters: list[tuple[str, str, dict]] = []
        if corpus_ids:
            from authora.services.export import tiptap_to_plain_text

            corpora_result = await db.execute(
                select(ComparisonCorpus).where(
                    ComparisonCorpus.id.in_(corpus_ids),
                    ComparisonCorpus.is_enabled.is_(True),
                )
            )
            corpora = list(corpora_result.scalars().all())
            for corpus in corpora:
                if corpus.project_id:
                    corpus_books = await db.execute(
                        select(Book).where(Book.project_id == corpus.project_id)
                    )
                    for book in corpus_books.scalars().all():
                        ch_result = await db.execute(
                            select(Chapter)
                            .where(Chapter.book_id == book.id, Chapter.deleted_at.is_(None))
                            .order_by(Chapter.sort_order)
                        )
                        for ch in ch_result.scalars().all():
                            text = tiptap_to_plain_text(ch.content) if ch.content else ""
                            corpus_chapters.append(
                                (
                                    str(ch.id),
                                    text,
                                    {"title": ch.title or "", "sort_order": ch.sort_order or 0},
                                )
                            )

        # Fallback: compare against other chapters in same book (self-similarity)
        if not corpus_chapters:
            corpus_chapters = query_chapters

        matches = compare_against_corpus(
            query_chapters,
            corpus_chapters,
            exclude_ranges=excluded_ranges,
            min_similarity=min_similarity,
        )

        total_chars = sum(len(t[1]) for t in query_chapters)
        overall_pct = compute_overall_similarity(matches, total_chars)

        chapter_id_map = {str(c.id): c.id for c in chapters}
        for m in matches:
            mp = MatchedPassage(
                scan_id=scan.id,
                chapter_id=chapter_id_map.get(m.query_chapter_id or "") if m.query_chapter_id else None,
                source_type=m.source_type,
                source_id=m.source_id,
                source_label=m.source_label,
                match_type=m.match_type,
                similarity_pct=m.similarity_pct,
                query_text=m.query_text,
                matched_text=m.matched_text,
                query_start=m.query_start,
                query_end=m.query_end,
            )
            db.add(mp)

        scan.status = "completed"
        scan.overall_similarity_pct = overall_pct
        scan.completed_at = datetime.now(timezone.utc)
    except Exception:
        scan.status = "failed"
        scan.completed_at = datetime.now(timezone.utc)
        raise

    return scan
