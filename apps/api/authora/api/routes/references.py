"""References API: Zotero, citation styles, bibliography, source notes, chapter citations."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_in_project_or_404, get_chapter_or_404, get_project_with_access_or_404
from authora.database import get_db
from authora.models import (
    Book,
    Chapter,
    ChapterCitation,
    CitationStyle,
    Project,
    ProjectCitationStyle,
    Source,
    SourceNote,
    ZoteroConnection,
)
from authora.services.csl_service import BUILTIN_STYLE_SLUGS, render_bibliography, render_citation
from authora.services.zotero_service import sync_zotero_to_project, verify_zotero_connection

router = APIRouter(prefix="/projects/{project_id}/references", tags=["references"])


# --- Schemas ---

class ZoteroConnectionCreate(BaseModel):
    library_type: str = Field(..., pattern="^(user|group)$")
    library_id: str = Field(..., min_length=1, max_length=50)
    api_key: str = Field(..., min_length=1, max_length=255)
    display_name: str | None = Field(None, max_length=255)


class ZoteroConnectionResponse(BaseModel):
    id: uuid.UUID
    library_type: str
    library_id: str
    display_name: str | None
    last_synced_at: str | None
    sync_status: str
    sync_error: str | None

    model_config = {"from_attributes": True}


class CitationStyleResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    is_builtin: bool

    model_config = {"from_attributes": True}


class ProjectCitationStyleUpdate(BaseModel):
    style_slug: str = Field(..., min_length=1)
    book_id: uuid.UUID | None = None


class BibliographyRequest(BaseModel):
    source_ids: list[uuid.UUID] = Field(..., min_length=1)
    style_slug: str = "apa"
    format_type: str = Field(default="plain", pattern="^(plain|html)$")


class CitationPreviewRequest(BaseModel):
    source_ids: list[uuid.UUID] = Field(..., min_length=1)
    style_slug: str = "apa"
    format_type: str = Field(default="plain", pattern="^(plain|html)$")


class ChapterCitationCreate(BaseModel):
    chapter_id: uuid.UUID
    source_id: uuid.UUID
    citation_key: str = Field(..., min_length=1, max_length=100)


class SourceNoteCreate(BaseModel):
    source_id: uuid.UUID
    content: str = Field(..., min_length=1)
    note_type: str = Field(default="annotation", max_length=50)
    page_ref: str | None = Field(None, max_length=100)


class SourceNoteResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    note_type: str
    content: str
    page_ref: str | None
    created_at: str

    model_config = {"from_attributes": True}


# --- Zotero connections (user-level, but scoped by project access) ---

@router.get("/zotero/connections", response_model=list[ZoteroConnectionResponse])
async def list_zotero_connections(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List user's Zotero connections."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(ZoteroConnection).where(ZoteroConnection.user_id == current_user.id)
    )
    conns = r.scalars().all()
    return [
        ZoteroConnectionResponse(
            id=c.id,
            library_type=c.library_type,
            library_id=c.library_id,
            display_name=c.display_name,
            last_synced_at=c.last_synced_at.isoformat() if c.last_synced_at else None,
            sync_status=c.sync_status,
            sync_error=c.sync_error,
        )
        for c in conns
    ]


@router.post("/zotero/connections", response_model=ZoteroConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_zotero_connection(
    project_id: uuid.UUID,
    data: ZoteroConnectionCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Connect a Zotero library. Verifies API key before saving."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    conn = ZoteroConnection(
        user_id=current_user.id,
        library_type=data.library_type,
        library_id=data.library_id,
        api_key=data.api_key,
        display_name=data.display_name,
    )
    db.add(conn)
    await db.flush()
    ok, msg = await verify_zotero_connection(conn)
    if not ok:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Zotero connection failed: {msg}")
    await db.commit()
    await db.refresh(conn)
    return ZoteroConnectionResponse(
        id=conn.id,
        library_type=conn.library_type,
        library_id=conn.library_id,
        display_name=conn.display_name,
        last_synced_at=conn.last_synced_at.isoformat() if conn.last_synced_at else None,
        sync_status=conn.sync_status,
        sync_error=conn.sync_error,
    )


@router.post("/zotero/connections/{conn_id}/sync")
async def sync_zotero(
    project_id: uuid.UUID,
    conn_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Sync Zotero library to project vault sources."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(ZoteroConnection).where(
            ZoteroConnection.id == conn_id,
            ZoteroConnection.user_id == current_user.id,
        )
    )
    conn = r.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zotero connection not found")
    synced, err = await sync_zotero_to_project(db, conn, project_id)
    if err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=err)
    await db.commit()
    return {"synced": synced, "message": f"Synced {synced} items"}


@router.delete("/zotero/connections/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zotero_connection(
    project_id: uuid.UUID,
    conn_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Disconnect Zotero. Sources remain but zotero_connection_id is cleared."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(ZoteroConnection).where(
            ZoteroConnection.id == conn_id,
            ZoteroConnection.user_id == current_user.id,
        )
    )
    conn = r.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zotero connection not found")
    await db.delete(conn)
    await db.commit()


# --- Citation styles ---

@router.get("/styles", response_model=list[CitationStyleResponse])
async def list_citation_styles(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List available citation styles (built-in + custom)."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(select(CitationStyle).order_by(CitationStyle.slug))
    styles = r.scalars().all()
    if not styles:
        return [
            CitationStyleResponse(id=uuid.uuid4(), slug=s, title=s.replace("-", " ").title(), is_builtin=True)
            for s in BUILTIN_STYLE_SLUGS
        ]
    return [CitationStyleResponse.model_validate(s) for s in styles]


@router.get("/styles/project")
async def get_project_citation_style(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
):
    """Get project or book citation style."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    q = select(ProjectCitationStyle).where(ProjectCitationStyle.project_id == project_id)
    if book_id:
        q = q.where(ProjectCitationStyle.book_id == book_id)
    else:
        q = q.where(ProjectCitationStyle.book_id.is_(None))
    r = await db.execute(q.order_by(ProjectCitationStyle.created_at.desc()).limit(1))
    pref = r.scalar_one_or_none()
    if not pref:
        return {"style_slug": "apa", "citation_style_id": None}
    style = await db.get(CitationStyle, pref.citation_style_id)
    return {"style_slug": style.slug if style else "apa", "citation_style_id": str(pref.citation_style_id)}


@router.put("/styles/project")
async def update_project_citation_style(
    project_id: uuid.UUID,
    data: ProjectCitationStyleUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Set project or book citation style."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    if data.book_id:
        await get_book_in_project_or_404(db, project_id, data.book_id)
    r = await db.execute(select(CitationStyle).where(CitationStyle.slug == data.style_slug))
    style = r.scalar_one_or_none()
    if not style:
        style = CitationStyle(slug=data.style_slug, title=data.style_slug.replace("-", " ").title(), is_builtin=True)
        db.add(style)
        await db.flush()
    existing = await db.execute(
        select(ProjectCitationStyle).where(
            ProjectCitationStyle.project_id == project_id,
            ProjectCitationStyle.book_id == data.book_id if data.book_id else None,
        )
    )
    pref = existing.scalar_one_or_none()
    if pref:
        pref.citation_style_id = style.id
    else:
        pref = ProjectCitationStyle(
            project_id=project_id,
            book_id=data.book_id,
            citation_style_id=style.id,
        )
        db.add(pref)
    await db.commit()
    return {"style_slug": style.slug}


# --- Bibliography & citation preview ---

@router.post("/bibliography")
async def generate_bibliography(
    project_id: uuid.UUID,
    data: BibliographyRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate bibliography from sources. Uses real CSL processing."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(Source).where(
            Source.project_id == project_id,
            Source.id.in_(data.source_ids),
        )
    )
    sources = r.scalars().all()
    if len(sources) != len(data.source_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some sources not found")
    refs = []
    for s in sources:
        csl = s.csl_json if hasattr(s, "csl_json") and s.csl_json else _source_to_csl(s)
        csl = dict(csl)
        csl["id"] = str(s.id)
        refs.append(csl)
    entries = render_bibliography(refs, citation_keys=[str(s.id) for s in sources], style_slug=data.style_slug, format_type=data.format_type)
    return {"entries": entries}


@router.post("/citation-preview")
async def preview_citation(
    project_id: uuid.UUID,
    data: CitationPreviewRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Preview in-text citation for given sources."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(Source).where(
            Source.project_id == project_id,
            Source.id.in_(data.source_ids),
        )
    )
    sources = r.scalars().all()
    if not sources:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sources not found")
    refs = []
    for s in sources:
        csl = s.csl_json if hasattr(s, "csl_json") and s.csl_json else _source_to_csl(s)
        csl["id"] = str(s.id)
        refs.append(csl)
    citation = render_citation(
        refs,
        citation_keys=[str(s.id) for s in sources],
        style_slug=data.style_slug,
        format_type=data.format_type,
    )
    return {"citation": citation}


def _source_to_csl(s: Source) -> dict:
    """Convert vault Source to minimal CSL JSON when csl_json not set."""
    return {
        "id": str(s.id),
        "type": "article-journal" if s.source_type == "article" else "book",
        "title": s.title,
        "author": [{"literal": s.author or "Unknown"}],
        "issued": {"date-parts": [[int(s.publication_date[:4])]] if s.publication_date and len(s.publication_date) >= 4 else [[0]]},
        "URL": s.url,
    }


# --- Chapter citations ---

@router.post("/citations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_chapter_citation(
    project_id: uuid.UUID,
    data: ChapterCitationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add citation to chapter. Links source to chapter."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    await get_chapter_or_404(db, data.chapter_id, project_id)
    r = await db.execute(
        select(Source).where(Source.project_id == project_id, Source.id == data.source_id)
    )
    src = r.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    cc = ChapterCitation(
        chapter_id=data.chapter_id,
        source_id=data.source_id,
        citation_key=data.citation_key,
    )
    db.add(cc)
    src.used_in_manuscript = True
    await db.commit()
    return {"id": str(cc.id), "chapter_id": str(data.chapter_id), "source_id": str(data.source_id)}


# --- Source notes ---

@router.post("/source-notes", response_model=SourceNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_source_note(
    project_id: uuid.UUID,
    data: SourceNoteCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add note/annotation to source."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    r = await db.execute(
        select(Source).where(Source.project_id == project_id, Source.id == data.source_id)
    )
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    note = SourceNote(
        source_id=data.source_id,
        user_id=current_user.id,
        content=data.content,
        note_type=data.note_type,
        page_ref=data.page_ref,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return SourceNoteResponse(
        id=note.id,
        source_id=note.source_id,
        note_type=note.note_type,
        content=note.content,
        page_ref=note.page_ref,
        created_at=note.created_at.isoformat(),
    )
