"""Shared resource resolvers - project, book, chapter. Reduces duplication across routes."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, Project, ProjectMember


async def get_project_or_404(db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    """Resolve project by ID, ensuring user ownership. Raises 404 if not found."""
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return p


async def get_project_with_access_or_404(
    db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[Project, str]:
    """Resolve project by ID, ensuring user has access (owner or member). Returns (project, role)."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if p.user_id == user_id:
        return p, "owner"
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return p, member.role


async def get_book_or_404(
    db: AsyncSession,
    book_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID | None = None,
) -> Book:
    """Resolve book by ID, ensuring user ownership via project. Optionally validate project_id."""
    q = select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
    if project_id is not None:
        q = q.where(Book.project_id == project_id)
    result = await db.execute(q)
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


async def get_book_with_access_or_404(
    db: AsyncSession,
    book_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Book:
    """Resolve book by ID within project, ensuring user has access (owner or member)."""
    await get_project_with_access_or_404(db, project_id, user_id)
    return await get_book_in_project_or_404(db, book_id, project_id)


async def get_fiction_book_or_404(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book:
    """Resolve fiction book. Raises 404 if not found or not fiction type."""
    book = await get_book_or_404(db, book_id, user_id)
    if book.type != "fiction":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not fiction")
    return book


async def get_nonfiction_book_or_404(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book:
    """Resolve nonfiction book. Raises 404 if not found or not nonfiction type."""
    book = await get_book_or_404(db, book_id, user_id)
    if book.type != "nonfiction":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not nonfiction")
    return book


async def get_book_in_project_or_404(
    db: AsyncSession, book_id: uuid.UUID, project_id: uuid.UUID
) -> Book:
    """Resolve book by ID within project. Raises 404 if not found."""
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.project_id == project_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


async def get_chapter_or_404(db: AsyncSession, book_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter:
    """Resolve chapter by ID within book. Raises 404 if not found."""
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter
