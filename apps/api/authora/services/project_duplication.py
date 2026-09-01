"""Project duplication service - copy project with books, chapters, notes, workspaces."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.models import (
    Book,
    BookSettings,
    Chapter,
    GhostwriterWorkspace,
    Note,
    NoteAttachment,
    Project,
    ProjectMember,
)
from authora.models.fiction import FictionWorkspace
from authora.models.nonfiction import NonfictionWorkspace


async def duplicate_project(db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID, new_name: str | None = None) -> Project | None:
    """Duplicate a project with all books, chapters, notes, and workspace data."""
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.books).selectinload(Book.chapters),
            selectinload(Project.books).selectinload(Book.ghostwriter_workspace),
            selectinload(Project.books).selectinload(Book.book_settings),
            selectinload(Project.notes).selectinload(Note.attachments),
        )
        .where(Project.id == project_id, Project.user_id == user_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        return None

    name = new_name or f"{src.name} (copy)"
    now = datetime.now(timezone.utc)
    new_project = Project(
        user_id=user_id,
        name=name,
        template_id=src.template_id,
        guidance_mode=getattr(src, "guidance_mode", "guided"),
        created_at=now,
        updated_at=now,
    )
    db.add(new_project)
    await db.flush()

    # Add owner as project member for collaboration consistency
    owner_member = ProjectMember(
        user_id=user_id,
        project_id=new_project.id,
        role="owner",
        invited_by=None,
    )
    db.add(owner_member)
    await db.flush()

    book_id_map: dict[uuid.UUID, uuid.UUID] = {}
    chapter_id_map: dict[uuid.UUID, uuid.UUID] = {}

    for book in src.books:
        if book.deleted_at:
            continue
        new_book = Book(
            project_id=new_project.id,
            title=book.title,
            genre=book.genre,
            genre_tags=list(book.genre_tags) if book.genre_tags else [],
            themes=list(book.themes) if book.themes else [],
            type=book.type,
            planner_data=dict(book.planner_data) if book.planner_data else None,
        )
        db.add(new_book)
        await db.flush()
        book_id_map[book.id] = new_book.id

        for ch in sorted(book.chapters, key=lambda c: c.sort_order):
            if ch.deleted_at:
                continue
            new_ch = Chapter(
                book_id=new_book.id,
                title=ch.title,
                sort_order=ch.sort_order,
                content=dict(ch.content) if ch.content else dict(),
                word_count=ch.word_count,
                section_status=ch.section_status,
                section_group=ch.section_group,
                tags=list(ch.tags) if ch.tags else [],
                content_source=ch.content_source,
            )
            db.add(new_ch)
            await db.flush()
            chapter_id_map[ch.id] = new_ch.id

        if book.ghostwriter_workspace:
            gw = book.ghostwriter_workspace
            new_gw = GhostwriterWorkspace(
                book_id=new_book.id,
                mode=gw.mode,
                workflow_step=gw.workflow_step,
                intake_answers=dict(gw.intake_answers) if gw.intake_answers else None,
                genre_tags=list(gw.genre_tags) if gw.genre_tags else [],
                themes=list(gw.themes) if gw.themes else [],
                voice_tone=gw.voice_tone,
                target_audience=gw.target_audience,
                desired_outcome=gw.desired_outcome,
                outline=dict(gw.outline) if gw.outline else None,
            )
            db.add(new_gw)

        if book.book_settings:
            bs = book.book_settings
            new_bs = BookSettings(
                book_id=new_book.id,
                settings=dict(bs.settings) if bs.settings else {},
            )
            db.add(new_bs)

    await db.flush()

    fw_result = await db.execute(
        select(FictionWorkspace).join(Book).join(Project).where(Project.id == project_id)
    )
    for fw in fw_result.scalars().all():
        if fw.book_id in book_id_map:
            new_fw = FictionWorkspace(
                book_id=book_id_map[fw.book_id],
                premise=fw.premise,
                genre=fw.genre,
                genre_tags=list(fw.genre_tags) if fw.genre_tags else [],
                tone=fw.tone,
                themes=fw.themes,
                pacing_notes=fw.pacing_notes,
            )
            db.add(new_fw)

    nf_result = await db.execute(
        select(NonfictionWorkspace).join(Book).join(Project).where(Project.id == project_id)
    )
    for nf in nf_result.scalars().all():
        if nf.book_id in book_id_map:
            new_nf = NonfictionWorkspace(
                book_id=book_id_map[nf.book_id],
                core_message=nf.core_message,
                reader_outcome=nf.reader_outcome,
                reader_promise=nf.reader_promise,
                topic=nf.topic,
            )
            db.add(new_nf)

    for note in src.notes:
        if note.deleted_at:
            continue
        new_book_id = book_id_map.get(note.book_id) if note.book_id else None
        new_chapter_id = chapter_id_map.get(note.chapter_id) if note.chapter_id else None
        new_note = Note(
            project_id=new_project.id,
            book_id=new_book_id,
            chapter_id=new_chapter_id,
            user_id=user_id,
            title=note.title,
            content=note.content,
            note_type=note.note_type,
            source=note.source,
            source_url=note.source_url,
            pinned=note.pinned,
            is_inspiration=note.is_inspiration,
            category=note.category,
            tags=list(note.tags) if note.tags else [],
            sort_order=note.sort_order,
        )
        db.add(new_note)
        await db.flush()
        for att in note.attachments:
            new_att = NoteAttachment(
                note_id=new_note.id,
                file_key=att.file_key,
                filename=att.filename,
                content_type=att.content_type,
                file_size=att.file_size,
            )
            db.add(new_att)

    await db.refresh(new_project)
    return new_project
