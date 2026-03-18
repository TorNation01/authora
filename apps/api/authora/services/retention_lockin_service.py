"""Retention and lock-in service: resume session, progress persistence, template dependency."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, Project, ProjectMember, ProjectTemplate, UserPreference

RESUME_SESSION_KEY = "resume_session"
RESUME_MAX_AGE_DAYS = 14


async def set_resume_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
) -> dict[str, Any]:
    """Store resume session in user preferences. Validates access."""
    project = await _get_project_with_access(db, project_id, user_id)
    if not project:
        raise ValueError("Project not found or access denied")

    book = await db.get(Book, book_id)
    if not book or book.project_id != project_id:
        raise ValueError("Book not found")

    chapter = await db.get(Chapter, chapter_id)
    if not chapter or chapter.book_id != book_id:
        raise ValueError("Chapter not found")

    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=user_id, preferences={})
        db.add(pref)

    now = datetime.now(timezone.utc)
    resume = {
        "project_id": str(project_id),
        "book_id": str(book_id),
        "chapter_id": str(chapter_id),
        "project_name": project.name,
        "book_title": book.title,
        "chapter_title": chapter.title or "Untitled",
        "updated_at": now.isoformat(),
    }
    merged = {**(pref.preferences or {}), RESUME_SESSION_KEY: resume}
    pref.preferences = merged
    await db.flush()
    return resume


async def get_resume_session(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> dict[str, Any] | None:
    """Get valid resume session (project, book, chapter) if exists and recent."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    pref = result.scalar_one_or_none()
    if not pref or not pref.preferences:
        return None

    resume = (pref.preferences or {}).get(RESUME_SESSION_KEY)
    if not resume or not isinstance(resume, dict):
        return None

    updated = resume.get("updated_at")
    if not updated:
        return None
    try:
        dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if datetime.now(timezone.utc) - dt > timedelta(days=RESUME_MAX_AGE_DAYS):
        return None

    project_id = resume.get("project_id")
    book_id = resume.get("book_id")
    chapter_id = resume.get("chapter_id")
    if not project_id or not book_id or not chapter_id:
        return None

    project = await _get_project_with_access(db, uuid.UUID(project_id), user_id)
    if not project:
        return None

    book = await db.get(Book, uuid.UUID(book_id))
    if not book or book.project_id != project.id:
        return None

    chapter = await db.get(Chapter, uuid.UUID(chapter_id))
    if not chapter or chapter.book_id != book.id:
        return None

    return {
        "project_id": str(project.id),
        "book_id": str(book.id),
        "chapter_id": str(chapter.id),
        "project_name": resume.get("project_name") or project.name,
        "book_title": resume.get("book_title") or book.title,
        "chapter_title": resume.get("chapter_title") or chapter.title or "Untitled",
        "updated_at": resume.get("updated_at"),
    }


async def _get_project_with_access(
    db: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Project | None:
    """Get project if user has access (owner or member). Returns None if not found."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        return None
    if p.user_id == user_id:
        return p
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if member_result.scalar_one_or_none():
        return p
    return None


async def get_template_info_for_project(
    db: AsyncSession,
    project: Project,
) -> dict[str, Any] | None:
    """Get template name/slug for project (template dependency lock-in)."""
    if not project.template_id:
        return None
    tpl = await db.get(ProjectTemplate, project.template_id)
    if not tpl or tpl.is_disabled:
        return None
    return {
        "template_id": str(tpl.id),
        "template_slug": tpl.slug,
        "template_name": tpl.name,
    }
