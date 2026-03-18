"""Marketplace service: template browsing with usage counts and creator info."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Project, ProjectTemplate, User


async def get_template_usage_counts(db: AsyncSession) -> dict[uuid.UUID, int]:
    """Return template_id -> total usage count (projects + books)."""
    # Projects using template
    r_proj = await db.execute(
        select(Project.template_id, func.count(Project.id).label("cnt"))
        .where(Project.template_id.isnot(None))
        .group_by(Project.template_id)
    )
    by_id: dict[uuid.UUID, int] = {tid: cnt for tid, cnt in r_proj.all()}

    # Books using template (may differ from project template)
    r_book = await db.execute(
        select(Book.template_id, func.count(Book.id).label("cnt"))
        .where(Book.template_id.isnot(None))
        .group_by(Book.template_id)
    )
    for tid, cnt in r_book.all():
        by_id[tid] = by_id.get(tid, 0) + cnt

    return by_id


async def get_creator_names(db: AsyncSession, creator_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    """Return creator_id -> display name (display_name or email)."""
    if not creator_ids:
        return {}
    r = await db.execute(
        select(User.id, User.display_name, User.email).where(User.id.in_(creator_ids))
    )
    return {
        row.id: (row.display_name or row.email or "Creator")
        for row in r.all()
    }
