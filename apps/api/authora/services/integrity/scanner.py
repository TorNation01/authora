"""Story Integrity Engine scanner/orchestrator."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, IntegrityIssue, IntegrityScan, Project
from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.chapter_analyzer import analyze_chapters
from authora.services.integrity.detectors import get_detectors_for_project
from authora.services.integrity.story_map import build_story_map


async def run_scan(
    db: AsyncSession,
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    scan_type: str = "full_project",
    triggered_by: str | None = None,
) -> IntegrityScan:
    """Run a full integrity scan on a book."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Project, Book)
        .join(Book, Book.project_id == Project.id)
        .options(
            selectinload(Project.vault_characters),
            selectinload(Project.vault_themes),
            selectinload(Project.timeline_events),
        )
        .where(Project.id == project_id, Book.id == book_id)
    )
    row = result.one_or_none()
    if not row:
        raise ValueError("Project or book not found")

    project, book = row
    chapters_result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None)).order_by(Chapter.sort_order)
    )
    chapters_orm = list(chapters_result.scalars().all())

    chapters_data = [
        {
            "id": str(ch.id),
            "title": ch.title,
            "content": ch.content,
            "word_count": ch.word_count,
            "sort_order": ch.sort_order,
        }
        for ch in chapters_orm
    ]

    vault_characters = []
    vault_themes = []
    vault_events = []
    if hasattr(project, "vault_characters") and project.vault_characters:
        vault_characters = [{"id": str(c.id), "full_name": c.full_name} for c in project.vault_characters]
    if hasattr(project, "vault_themes") and project.vault_themes:
        vault_themes = [{"id": str(t.id), "name": t.name} for t in project.vault_themes]
    if hasattr(project, "timeline_events") and project.timeline_events:
        vault_events = [{"id": str(e.id), "title": e.title} for e in project.timeline_events]

    project_type = getattr(project, "knowledge_mode", None) or book.type or "fiction"
    guidance_mode = getattr(project, "guidance_mode", "flexible")

    story_map = build_story_map(
        chapters=chapters_data,
        project_knowledge_mode=project_type,
        book_type=book.type or "fiction",
        planner_data=book.planner_data,
        vault_characters=vault_characters,
        vault_themes=vault_themes,
        vault_events=vault_events,
    )
    story_map["guidance_mode"] = guidance_mode

    chapter_health = analyze_chapters(chapters_data, story_map, project_type=project_type, guidance_mode=guidance_mode)
    story_map["chapter_health"] = chapter_health

    scan = IntegrityScan(
        id=uuid.uuid4(),
        project_id=project_id,
        book_id=book_id,
        scan_type=scan_type,
        status="running",
        triggered_by=triggered_by,
        chapter_count=len(chapters_orm),
        story_map_snapshot=story_map,
    )
    db.add(scan)
    await db.flush()

    start = time.perf_counter()
    detector_classes = get_detectors_for_project(project_type, guidance_mode)
    all_issues: list[dict[str, Any]] = []
    detector_config = {"project_type": project_type, "guidance_mode": guidance_mode}

    for DetectorCls in detector_classes:
        detector = DetectorCls(story_map=story_map, chapters=chapters_data, config=detector_config)
        issues = detector.detect()
        all_issues.extend(issues)

    for ch_health in chapter_health:
        for iss in ch_health.get("issues", []):
            all_issues.append({
                "issue_type": iss.get("type", "chapter_issue"),
                "category": "structure",
                "severity": iss.get("severity", "low"),
                "title": iss.get("title", "Chapter issue"),
                "description": iss.get("suggestion"),
                "chapter_id": ch_health.get("chapter_id"),
                "fix_suggestions": [{"action": iss.get("type"), "label": iss.get("suggestion", "")}],
                "confidence": 0.7,
            })

    for issue_data in all_issues:
        ch_id = issue_data.get("chapter_id")
        try:
            chapter_id = uuid.UUID(ch_id) if ch_id else None
        except (ValueError, TypeError):
            chapter_id = None
        issue = IntegrityIssue(
            id=uuid.uuid4(),
            scan_id=scan.id,
            project_id=project_id,
            book_id=book_id,
            chapter_id=chapter_id,
            issue_type=issue_data["issue_type"],
            category=issue_data["category"],
            severity=issue_data["severity"],
            confidence=issue_data.get("confidence", 0.8),
            title=issue_data["title"],
            description=issue_data.get("description"),
            location_hint=issue_data.get("location_hint"),
            related_chapter_ids=issue_data.get("related_chapter_ids"),
            fix_suggestions=issue_data.get("fix_suggestions"),
        )
        db.add(issue)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    scan.status = "completed"
    scan.completed_at = datetime.now(timezone.utc)
    scan.duration_ms = elapsed_ms
    scan.issue_count = len(all_issues)

    return scan
