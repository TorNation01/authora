"""Originality, similarity, AI-assistance, and AI-origin risk API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_with_access_or_404
from authora.database import get_db
from authora.models import (
    AIAssistanceDisclosure,
    AIOriginRiskReview,
    ComparisonCorpus,
    IntegrityReviewComment,
    IntegrityReviewReport,
    MatchedPassage,
    OriginalityAdminConfig,
    OriginalityScan,
)
from authora.schemas.originality import (
    AIAssistanceDisclosureCreate,
    AIAssistanceDisclosureResponse,
    AIOriginRiskResponse,
    ComparisonCorpusCreate,
    ComparisonCorpusResponse,
    IntegrityReviewCommentCreate,
    IntegrityReviewCommentResponse,
    IntegrityReviewReportCreate,
    IntegrityReviewReportResponse,
    IntegrityReviewReportUpdate,
    MatchedPassageResponse,
    OriginalityReportSummary,
    OriginalityScanCreate,
    OriginalityScanResponse,
)
from authora.services.originality import run_ai_origin_risk_review
from authora.services.originality.scan_service import run_originality_scan

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}", tags=["originality"])


async def _originality_enabled(db: AsyncSession) -> bool:
    """Check if originality features are enabled."""
    result = await db.execute(
        select(OriginalityAdminConfig).where(OriginalityAdminConfig.key == "originality_enabled")
    )
    row = result.scalar_one_or_none()
    if row and isinstance(row.value, dict) and "enabled" in row.value:
        return bool(row.value["enabled"])
    return True


# --- Corpora ---


@router.get("/originality/corpora", response_model=list[ComparisonCorpusResponse])
async def list_corpora(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List comparison corpora available for the project."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")
    result = await db.execute(
        select(ComparisonCorpus)
        .where(
            (ComparisonCorpus.user_id == current_user.id) | (ComparisonCorpus.project_id == project_id),
            ComparisonCorpus.is_enabled.is_(True),
        )
    )
    return list(result.scalars().all())


@router.post("/originality/corpora", response_model=ComparisonCorpusResponse, status_code=status.HTTP_201_CREATED)
async def create_corpus(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    body: ComparisonCorpusCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create comparison corpus."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")
    corpus = ComparisonCorpus(
        project_id=body.project_id or project_id,
        user_id=current_user.id,
        corpus_type=body.corpus_type,
        name=body.name,
        description=body.description,
    )
    db.add(corpus)
    await db.commit()
    await db.refresh(corpus)
    return corpus


# --- Scans ---


@router.post("/originality/scan", response_model=OriginalityScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    body: OriginalityScanCreate | None = None,
    current_user: CurrentUser = Depends(),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(),
):
    """Run originality/similarity scan. Results are review aids only."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")
    body = body or OriginalityScanCreate()
    scan = await run_originality_scan(
        db,
        project_id=project_id,
        book_id=book_id,
        created_by=current_user.id,
        corpus_ids=body.corpus_ids,
        excluded_ranges=body.excluded_ranges,
        min_similarity=body.min_similarity,
    )
    await db.commit()
    await db.refresh(scan)
    return scan


@router.get("/originality/scans", response_model=list[OriginalityScanResponse])
async def list_scans(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    """List originality scans for the book."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")
    result = await db.execute(
        select(OriginalityScan)
        .where(OriginalityScan.book_id == book_id)
        .order_by(OriginalityScan.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/originality/scans/{scan_id}", response_model=OriginalityScanResponse)
async def get_scan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    scan_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get single originality scan."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(OriginalityScan).where(
            OriginalityScan.id == scan_id,
            OriginalityScan.book_id == book_id,
        )
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


@router.get("/originality/scans/{scan_id}/passages", response_model=list[MatchedPassageResponse])
async def list_matched_passages(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    scan_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    chapter_id: uuid.UUID | None = Query(None),
):
    """List matched passages for a scan."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    q = select(MatchedPassage).where(MatchedPassage.scan_id == scan_id)
    if chapter_id:
        q = q.where(MatchedPassage.chapter_id == chapter_id)
    result = await db.execute(q)
    passages = list(result.scalars().all())
    scan_result = await db.execute(select(OriginalityScan).where(OriginalityScan.id == scan_id, OriginalityScan.book_id == book_id))
    if not scan_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return passages


# --- AI-assistance disclosure ---


@router.get("/originality/ai-assistance", response_model=list[AIAssistanceDisclosureResponse])
async def list_ai_assistance(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    chapter_id: uuid.UUID | None = Query(None),
):
    """List AI-assistance disclosures for the book."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    q = select(AIAssistanceDisclosure).where(
        AIAssistanceDisclosure.project_id == project_id,
        (AIAssistanceDisclosure.book_id == book_id) | (AIAssistanceDisclosure.book_id.is_(None)),
    )
    if chapter_id:
        q = q.where(AIAssistanceDisclosure.chapter_id == chapter_id)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.post("/originality/ai-assistance", response_model=AIAssistanceDisclosureResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_assistance(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    body: AIAssistanceDisclosureCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create AI-assistance disclosure."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    disclosure = AIAssistanceDisclosure(
        project_id=project_id,
        book_id=body.book_id or book_id,
        chapter_id=body.chapter_id,
        user_id=current_user.id,
        disclosure_type=body.disclosure_type,
        content_source=body.content_source,
        ai_action_id=body.ai_action_id,
        section_hint=body.section_hint,
        notes=body.notes,
    )
    db.add(disclosure)
    await db.commit()
    await db.refresh(disclosure)
    return disclosure


# --- AI-origin risk ---


@router.get("/originality/ai-origin-risk", response_model=AIOriginRiskResponse)
async def get_ai_origin_risk(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get AI-origin risk review. Probabilistic, review-aid only. Not a detector."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")
    from authora.models import Chapter, Book

    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    ch_result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
    )
    chapters = [
        {"content_source": ch.content_source, "id": str(ch.id)}
        for ch in ch_result.scalars().all()
    ]
    risk = await run_ai_origin_risk_review(db, str(project_id), str(book_id), chapters)
    return AIOriginRiskResponse(
        risk_band=risk.risk_band,
        confidence_low=risk.confidence_low,
        confidence_high=risk.confidence_high,
        signals_summary=risk.signals_summary,
        disclaimer=risk.disclaimer,
    )


# --- Review reports ---


@router.get("/originality/reports", response_model=list[IntegrityReviewReportResponse])
async def list_review_reports(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List integrity review reports for the book."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityReviewReport)
        .where(IntegrityReviewReport.book_id == book_id)
        .order_by(IntegrityReviewReport.updated_at.desc())
    )
    return list(result.scalars().all())


@router.post("/originality/reports", response_model=IntegrityReviewReportResponse, status_code=status.HTTP_201_CREATED)
async def create_review_report(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    body: IntegrityReviewReportCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create integrity review report."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    report = IntegrityReviewReport(
        project_id=project_id,
        book_id=book_id,
        originality_scan_id=body.originality_scan_id,
        reviewer_id=current_user.id,
        needs_human_review=body.needs_human_review,
        reviewer_notes=body.reviewer_notes,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.patch("/originality/reports/{report_id}", response_model=IntegrityReviewReportResponse)
async def update_review_report(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    report_id: uuid.UUID,
    body: IntegrityReviewReportUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update integrity review report."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityReviewReport).where(
            IntegrityReviewReport.id == report_id,
            IntegrityReviewReport.book_id == book_id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if body.originality_scan_id is not None:
        report.originality_scan_id = body.originality_scan_id
    if body.needs_human_review is not None:
        report.needs_human_review = body.needs_human_review
    if body.reviewer_notes is not None:
        report.reviewer_notes = body.reviewer_notes
    report.status = "updated"
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/originality/reports/{report_id}/comments", response_model=IntegrityReviewCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_review_comment(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    report_id: uuid.UUID,
    body: IntegrityReviewCommentCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add comment to review report."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    report_result = await db.execute(
        select(IntegrityReviewReport).where(
            IntegrityReviewReport.id == report_id,
            IntegrityReviewReport.book_id == book_id,
        )
    )
    if not report_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    comment = IntegrityReviewComment(
        report_id=report_id,
        matched_passage_id=body.matched_passage_id,
        comment_type=body.comment_type,
        content=body.content,
        author_id=current_user.id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


# --- Full report ---


@router.get("/originality/report", response_model=OriginalityReportSummary)
async def get_full_report(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    scan_id: uuid.UUID | None = Query(None, description="Latest scan if omitted"),
):
    """Get full originality report (scan, passages, AI-assistance, AI-origin risk, review)."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    if not await _originality_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Originality features are disabled")

    if scan_id:
        scan_result = await db.execute(
            select(OriginalityScan).where(
                OriginalityScan.id == scan_id,
                OriginalityScan.book_id == book_id,
            )
        )
    else:
        scan_result = await db.execute(
            select(OriginalityScan)
            .where(OriginalityScan.book_id == book_id)
            .order_by(OriginalityScan.started_at.desc())
            .limit(1)
        )
    scan = scan_result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scan found")

    passages_result = await db.execute(select(MatchedPassage).where(MatchedPassage.scan_id == scan.id))
    passages = list(passages_result.scalars().all())

    disclosures_result = await db.execute(
        select(AIAssistanceDisclosure).where(
            AIAssistanceDisclosure.project_id == project_id,
            (AIAssistanceDisclosure.book_id == book_id) | (AIAssistanceDisclosure.book_id.is_(None)),
        )
    )
    disclosures = list(disclosures_result.scalars().all())

    from authora.models import Chapter, Book

    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    chapters = []
    if book:
        ch_result = await db.execute(
            select(Chapter).where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
        )
        chapters = [{"content_source": ch.content_source, "id": str(ch.id)} for ch in ch_result.scalars().all()]
    risk_result = await run_ai_origin_risk_review(db, str(project_id), str(book_id), chapters)
    ai_risk = AIOriginRiskResponse(
        risk_band=risk_result.risk_band,
        confidence_low=risk_result.confidence_low,
        confidence_high=risk_result.confidence_high,
        signals_summary=risk_result.signals_summary,
        disclaimer=risk_result.disclaimer,
    )

    report_result = await db.execute(
        select(IntegrityReviewReport)
        .where(IntegrityReviewReport.book_id == book_id, IntegrityReviewReport.originality_scan_id == scan.id)
        .order_by(IntegrityReviewReport.updated_at.desc())
        .limit(1)
    )
    review_report = report_result.scalar_one_or_none()

    return OriginalityReportSummary(
        scan=scan,
        matched_passages=passages,
        ai_assistance_disclosures=disclosures,
        ai_origin_risk=ai_risk,
        review_report=review_report,
    )
