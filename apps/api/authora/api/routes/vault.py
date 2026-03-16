"""AUTHORA vault API: ideas, research, characters, locations, timeline, themes, sources, chapter knowledge."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import (
    get_book_in_project_or_404,
    get_chapter_or_404,
    get_project_with_access_or_404,
)
from authora.database import get_db
from authora.models import (
    Book,
    Chapter,
    ChapterCharacterLink,
    ChapterEventLink,
    ChapterLocationLink,
    ChapterResearchLink,
    ChapterSourceLink,
    ChapterThemeLink,
    Idea,
    Project,
    ResearchEntry,
    Source,
    Theme,
    TimelineEvent,
    VaultCharacter,
    VaultLocation,
    VaultRelationship,
)
from authora.schemas.vault import (
    ChapterCharacterLinkCreate,
    ChapterCharacterLinkResponse,
    ChapterEventLinkCreate,
    ChapterEventLinkResponse,
    ChapterKnowledgePanel,
    ChapterLocationLinkCreate,
    ChapterLocationLinkResponse,
    ChapterResearchLinkCreate,
    ChapterResearchLinkResponse,
    ChapterSourceLinkCreate,
    ChapterSourceLinkResponse,
    ChapterThemeLinkCreate,
    ChapterThemeLinkResponse,
    IdeaCreate,
    IdeaResponse,
    IdeaUpdate,
    ResearchEntryCreate,
    ResearchEntryResponse,
    ResearchEntryUpdate,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    ThemeCreate,
    ThemeResponse,
    ThemeUpdate,
    TimelineEventCreate,
    TimelineEventResponse,
    TimelineEventUpdate,
    VaultCharacterCreate,
    VaultCharacterResponse,
    VaultCharacterUpdate,
    VaultLocationCreate,
    VaultLocationResponse,
    VaultLocationUpdate,
    VaultRelationshipCreate,
    VaultRelationshipResponse,
    VaultRelationshipUpdate,
)

router = APIRouter(prefix="/projects/{project_id}/vault", tags=["vault"])


async def _ensure_project_access(db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID):
    await get_project_with_access_or_404(db, project_id, user_id)


# --- Knowledge mode config ---

@router.get("/config")
async def get_vault_config(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get vault config for project: knowledge_mode, enabled modules, module labels. UI uses this to show/hide panels."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    enabled = get_enabled_modules(project.knowledge_mode, project.knowledge_modules)
    modules_with_labels = [{"id": m, "label": get_module_label(m)} for m in enabled]
    return {
        "knowledge_mode": project.knowledge_mode,
        "knowledge_modules_override": project.knowledge_modules is not None and len(project.knowledge_modules or []) > 0,
        "enabled_modules": enabled,
        "modules_with_labels": modules_with_labels,
        "available_modes": ["fiction", "nonfiction", "memoir", "workbook", "hybrid"],
        "default_modules_by_mode": KNOWLEDGE_MODULE_DEFAULTS,
        "all_module_labels": KNOWLEDGE_MODULE_LABELS,
    }


@router.patch("/config")
async def update_vault_config(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    knowledge_mode: str | None = Query(None, pattern="^(fiction|nonfiction|memoir|workbook|hybrid)$"),
    knowledge_modules: list[str] | None = None,
):
    """Update vault config: knowledge_mode and/or enabled modules. Pass knowledge_modules=[] to clear override."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if data.knowledge_mode is not None:
        if data.knowledge_mode not in ("fiction", "nonfiction", "memoir", "workbook", "hybrid"):
            raise HTTPException(status_code=400, detail="Invalid knowledge_mode")
        project.knowledge_mode = data.knowledge_mode
    if data.knowledge_modules is not None:
        project.knowledge_modules = data.knowledge_modules if data.knowledge_modules else None
    await db.flush()
    await db.refresh(project)
    enabled = get_enabled_modules(project.knowledge_mode, project.knowledge_modules)
    return {
        "knowledge_mode": project.knowledge_mode,
        "enabled_modules": enabled,
    }


# --- Vault Search (AI-assisted retrieval) ---

@router.get("/search")
async def vault_search(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., min_length=1),
    character_id: uuid.UUID | None = Query(None, description="Filter by character"),
    chapter_id: uuid.UUID | None = Query(None, description="Filter by chapter"),
    location_id: uuid.UUID | None = Query(None, description="Filter by location"),
    entity_types: str | None = Query(None, description="Comma-separated: idea,research,character,location,theme,source,event"),
    status: str | None = Query(None, description="For ideas: raw_idea, maybe_later, planned, used, archived"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search vault: ideas, research, characters, locations, themes, sources, events. Use for AI-assisted retrieval."""
    await _ensure_project_access(db, project_id, current_user.id)
    term = f"%{q.strip()}%"
    types = [t.strip() for t in entity_types.split(",")] if entity_types else ["idea", "research", "character", "location", "theme", "source", "event"]

    results: dict[str, list] = {
        "ideas": [],
        "research": [],
        "characters": [],
        "locations": [],
        "themes": [],
        "sources": [],
        "events": [],
    }

    if "idea" in types:
        stmt = select(Idea).where(Idea.project_id == project_id)
        stmt = stmt.where(Idea.title.ilike(term) | Idea.content.ilike(term))
        if character_id:
            stmt = stmt.where(Idea.character_id == character_id)
        if chapter_id:
            stmt = stmt.where(Idea.chapter_id == chapter_id)
        if location_id:
            stmt = stmt.where(Idea.location_id == location_id)
        if status:
            stmt = stmt.where(Idea.status == status)
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["ideas"] = [IdeaResponse.model_validate(i) for i in r.scalars().all()]

    if "research" in types:
        stmt = select(ResearchEntry).where(ResearchEntry.project_id == project_id)
        stmt = stmt.where(ResearchEntry.title.ilike(term) | ResearchEntry.content.ilike(term))
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["research"] = [ResearchEntryResponse.model_validate(e) for e in r.scalars().all()]

    if "character" in types:
        stmt = select(VaultCharacter).where(VaultCharacter.project_id == project_id)
        stmt = stmt.where(
            VaultCharacter.full_name.ilike(term)
            | (VaultCharacter.role_in_story or "").ilike(term)
            | (VaultCharacter.backstory or "").ilike(term)
            | (VaultCharacter.goals or "").ilike(term)
        )
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["characters"] = [VaultCharacterResponse.model_validate(c) for c in r.scalars().all()]

    if "location" in types:
        stmt = select(VaultLocation).where(VaultLocation.project_id == project_id)
        stmt = stmt.where(
            VaultLocation.name.ilike(term)
            | (VaultLocation.description or "").ilike(term)
            | (VaultLocation.history or "").ilike(term)
        )
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["locations"] = [VaultLocationResponse.model_validate(l) for l in r.scalars().all()]

    if "theme" in types:
        stmt = select(Theme).where(Theme.project_id == project_id)
        stmt = stmt.where(Theme.name.ilike(term) | (Theme.description or "").ilike(term))
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["themes"] = [ThemeResponse.model_validate(t) for t in r.scalars().all()]

    if "source" in types:
        stmt = select(Source).where(Source.project_id == project_id)
        stmt = stmt.where(
            Source.title.ilike(term)
            | (Source.author or "").ilike(term)
            | (Source.usage_notes or "").ilike(term)
        )
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["sources"] = [SourceResponse.model_validate(s) for s in r.scalars().all()]

    if "event" in types:
        stmt = select(TimelineEvent).where(TimelineEvent.project_id == project_id)
        stmt = stmt.where(TimelineEvent.title.ilike(term) | (TimelineEvent.description or "").ilike(term))
        stmt = stmt.limit(limit)
        r = await db.execute(stmt)
        results["events"] = [TimelineEventResponse.model_validate(e) for e in r.scalars().all()]

    return {"query": q, "results": results}


# --- Ideas ---

@router.get("/ideas", response_model=list[IdeaResponse])
async def list_ideas(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    idea_type: str | None = Query(None),
    status: str | None = Query(None),
    book_id: uuid.UUID | None = Query(None),
    chapter_id: uuid.UUID | None = Query(None),
    pinned: bool | None = Query(None),
    starred: bool | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List ideas for project with optional filters."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(Idea).where(Idea.project_id == project_id)
    if idea_type:
        stmt = stmt.where(Idea.idea_type == idea_type)
    if status:
        stmt = stmt.where(Idea.status == status)
    if book_id is not None:
        stmt = stmt.where(Idea.book_id == book_id)
    if chapter_id is not None:
        stmt = stmt.where(Idea.chapter_id == chapter_id)
    if pinned is not None:
        stmt = stmt.where(Idea.pinned == pinned)
    if starred is not None:
        stmt = stmt.where(Idea.starred == starred)
    if q and q.strip():
        stmt = stmt.where(
            Idea.title.ilike(f"%{q.strip()}%") | Idea.content.ilike(f"%{q.strip()}%")
        )
    stmt = stmt.order_by(Idea.pinned.desc(), Idea.starred.desc(), Idea.updated_at.desc()).limit(limit)
    result = await db.execute(stmt)
    ideas = result.scalars().all()
    return [IdeaResponse.model_validate(i) for i in ideas]


@router.post("/ideas", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    project_id: uuid.UUID,
    data: IdeaCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create idea."""
    await _ensure_project_access(db, project_id, current_user.id)
    idea = Idea(
        project_id=project_id,
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        idea_type=data.idea_type,
        status=data.status,
        pinned=data.pinned,
        starred=data.starred,
        category=data.category,
        tags=data.tags or [],
        book_id=data.book_id,
        chapter_id=data.chapter_id,
        character_id=data.character_id,
        location_id=data.location_id,
        timeline_event_id=data.timeline_event_id,
        metadata_=data.metadata,
    )
    db.add(idea)
    await db.flush()
    from authora.services.onboarding_analytics import record_first_idea_captured

    await record_first_idea_captured(db, current_user.id)
    await db.refresh(idea)
    return IdeaResponse.model_validate(idea)


@router.get("/ideas/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    project_id: uuid.UUID,
    idea_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get idea by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(select(Idea).where(Idea.id == idea_id, Idea.project_id == project_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    return IdeaResponse.model_validate(idea)


@router.patch("/ideas/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    project_id: uuid.UUID,
    idea_id: uuid.UUID,
    data: IdeaUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update idea."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(select(Idea).where(Idea.id == idea_id, Idea.project_id == project_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "metadata":
            setattr(idea, "metadata_", v)
        else:
            setattr(idea, k, v)
    await db.flush()
    await db.refresh(idea)
    return IdeaResponse.model_validate(idea)


@router.delete("/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(
    project_id: uuid.UUID,
    idea_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete idea."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(select(Idea).where(Idea.id == idea_id, Idea.project_id == project_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    await db.delete(idea)


# --- Research ---

@router.get("/research", response_model=list[ResearchEntryResponse])
async def list_research(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_type: str | None = Query(None),
    topic: str | None = Query(None),
    needs_verification: bool | None = Query(None),
    parent_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List research entries."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(ResearchEntry).where(ResearchEntry.project_id == project_id)
    if entry_type:
        stmt = stmt.where(ResearchEntry.entry_type == entry_type)
    if topic:
        stmt = stmt.where(ResearchEntry.topic == topic)
    if needs_verification is not None:
        stmt = stmt.where(ResearchEntry.needs_verification == needs_verification)
    if parent_id is not None:
        stmt = stmt.where(ResearchEntry.parent_id == parent_id)
    stmt = stmt.order_by(ResearchEntry.sort_order.asc(), ResearchEntry.updated_at.desc()).limit(limit)
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return [ResearchEntryResponse.model_validate(e) for e in entries]


@router.post("/research", response_model=ResearchEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_research(
    project_id: uuid.UUID,
    data: ResearchEntryCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create research entry."""
    await _ensure_project_access(db, project_id, current_user.id)
    entry = ResearchEntry(
        project_id=project_id,
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        entry_type=data.entry_type,
        topic=data.topic,
        tags=data.tags or [],
        needs_verification=data.needs_verification,
        parent_id=data.parent_id,
        source_id=data.source_id,
        link_metadata=data.link_metadata,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return ResearchEntryResponse.model_validate(entry)


@router.get("/research/{entry_id}", response_model=ResearchEntryResponse)
async def get_research(
    project_id: uuid.UUID,
    entry_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get research entry by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(ResearchEntry).where(
            ResearchEntry.id == entry_id, ResearchEntry.project_id == project_id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    return ResearchEntryResponse.model_validate(entry)


@router.patch("/research/{entry_id}", response_model=ResearchEntryResponse)
async def update_research(
    project_id: uuid.UUID,
    entry_id: uuid.UUID,
    data: ResearchEntryUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update research entry."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(ResearchEntry).where(
            ResearchEntry.id == entry_id, ResearchEntry.project_id == project_id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(entry, k, v)
    await db.flush()
    await db.refresh(entry)
    return ResearchEntryResponse.model_validate(entry)


@router.delete("/research/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research(
    project_id: uuid.UUID,
    entry_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete research entry."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(ResearchEntry).where(
            ResearchEntry.id == entry_id, ResearchEntry.project_id == project_id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    await db.delete(entry)


# --- Characters ---

@router.get("/characters", response_model=list[VaultCharacterResponse])
async def list_characters(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List characters."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(VaultCharacter).where(VaultCharacter.project_id == project_id)
    if book_id is not None:
        stmt = stmt.where(VaultCharacter.book_id == book_id)
    if status:
        stmt = stmt.where(VaultCharacter.status == status)
    stmt = stmt.order_by(VaultCharacter.sort_order.asc(), VaultCharacter.full_name.asc()).limit(limit)
    result = await db.execute(stmt)
    chars = result.scalars().all()
    return [VaultCharacterResponse.model_validate(c) for c in chars]


@router.post("/characters", response_model=VaultCharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: uuid.UUID,
    data: VaultCharacterCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create character."""
    await _ensure_project_access(db, project_id, current_user.id)
    char = VaultCharacter(
        project_id=project_id,
        full_name=data.full_name,
        aliases=data.aliases or [],
        role_in_story=data.role_in_story,
        archetype=data.archetype,
        age=data.age,
        appearance_notes=data.appearance_notes,
        voice_notes=data.voice_notes,
        personality_traits=data.personality_traits,
        goals=data.goals,
        fears=data.fears,
        motivations=data.motivations,
        internal_conflict=data.internal_conflict,
        external_conflict=data.external_conflict,
        backstory=data.backstory,
        timeline_notes=data.timeline_notes,
        secrets=data.secrets,
        quirks=data.quirks,
        dialogue_patterns=data.dialogue_patterns,
        emotional_arc=data.emotional_arc,
        private_notes=data.private_notes,
        status=data.status,
        book_id=data.book_id,
    )
    db.add(char)
    await db.flush()
    await db.refresh(char)
    return VaultCharacterResponse.model_validate(char)


@router.get("/characters/{character_id}", response_model=VaultCharacterResponse)
async def get_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get character by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultCharacter).where(
            VaultCharacter.id == character_id, VaultCharacter.project_id == project_id
        )
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return VaultCharacterResponse.model_validate(char)


@router.patch("/characters/{character_id}", response_model=VaultCharacterResponse)
async def update_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    data: VaultCharacterUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update character."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultCharacter).where(
            VaultCharacter.id == character_id, VaultCharacter.project_id == project_id
        )
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(char, k, v)
    await db.flush()
    await db.refresh(char)
    return VaultCharacterResponse.model_validate(char)


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    project_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete character."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultCharacter).where(
            VaultCharacter.id == character_id, VaultCharacter.project_id == project_id
        )
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    await db.delete(char)


# --- Locations ---

@router.get("/locations", response_model=list[VaultLocationResponse])
async def list_locations(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
    category: str | None = Query(None),
    parent_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List locations/settings."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(VaultLocation).where(VaultLocation.project_id == project_id)
    if book_id is not None:
        stmt = stmt.where(VaultLocation.book_id == book_id)
    if category:
        stmt = stmt.where(VaultLocation.category == category)
    if parent_id is not None:
        stmt = stmt.where(VaultLocation.parent_id == parent_id)
    stmt = stmt.order_by(VaultLocation.sort_order.asc(), VaultLocation.name.asc()).limit(limit)
    result = await db.execute(stmt)
    locs = result.scalars().all()
    return [VaultLocationResponse.model_validate(l) for l in locs]


@router.post("/locations", response_model=VaultLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    project_id: uuid.UUID,
    data: VaultLocationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create location/setting."""
    await _ensure_project_access(db, project_id, current_user.id)
    loc = VaultLocation(
        project_id=project_id,
        name=data.name,
        category=data.category,
        description=data.description,
        rules=data.rules,
        geography=data.geography,
        environment=data.environment,
        atmosphere=data.atmosphere,
        history=data.history,
        constraints=data.constraints,
        book_id=data.book_id,
        parent_id=data.parent_id,
    )
    db.add(loc)
    await db.flush()
    await db.refresh(loc)
    return VaultLocationResponse.model_validate(loc)


@router.get("/locations/{location_id}", response_model=VaultLocationResponse)
async def get_location(
    project_id: uuid.UUID,
    location_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get location by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultLocation).where(
            VaultLocation.id == location_id, VaultLocation.project_id == project_id
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return VaultLocationResponse.model_validate(loc)


@router.patch("/locations/{location_id}", response_model=VaultLocationResponse)
async def update_location(
    project_id: uuid.UUID,
    location_id: uuid.UUID,
    data: VaultLocationUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update location."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultLocation).where(
            VaultLocation.id == location_id, VaultLocation.project_id == project_id
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)
    await db.flush()
    await db.refresh(loc)
    return VaultLocationResponse.model_validate(loc)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    project_id: uuid.UUID,
    location_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete location."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultLocation).where(
            VaultLocation.id == location_id, VaultLocation.project_id == project_id
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    await db.delete(loc)


# --- Timeline Events ---

@router.get("/timeline", response_model=list[TimelineEventResponse])
async def list_timeline_events(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
    event_type: str | None = Query(None),
    storyline: str | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List timeline events."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(TimelineEvent).where(TimelineEvent.project_id == project_id)
    if book_id is not None:
        stmt = stmt.where(TimelineEvent.book_id == book_id)
    if event_type:
        stmt = stmt.where(TimelineEvent.event_type == event_type)
    if storyline:
        stmt = stmt.where(TimelineEvent.storyline == storyline)
    stmt = stmt.order_by(TimelineEvent.sequence_order.asc(), TimelineEvent.event_date.asc().nullslast())
    result = await db.execute(stmt)
    events = result.scalars().all()
    return [TimelineEventResponse.model_validate(e) for e in events]


@router.post("/timeline", response_model=TimelineEventResponse, status_code=status.HTTP_201_CREATED)
async def create_timeline_event(
    project_id: uuid.UUID,
    data: TimelineEventCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create timeline event."""
    await _ensure_project_access(db, project_id, current_user.id)
    evt = TimelineEvent(
        project_id=project_id,
        title=data.title,
        description=data.description,
        event_type=data.event_type,
        event_date=data.event_date,
        date_label=data.date_label,
        sequence_order=data.sequence_order,
        storyline=data.storyline,
        time_period=data.time_period,
        book_id=data.book_id,
    )
    db.add(evt)
    await db.flush()
    await db.refresh(evt)
    return TimelineEventResponse.model_validate(evt)


@router.get("/timeline/{event_id}", response_model=TimelineEventResponse)
async def get_timeline_event(
    project_id: uuid.UUID,
    event_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get timeline event by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.project_id == project_id
        )
    )
    evt = result.scalar_one_or_none()
    if not evt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found")
    return TimelineEventResponse.model_validate(evt)


@router.patch("/timeline/{event_id}", response_model=TimelineEventResponse)
async def update_timeline_event(
    project_id: uuid.UUID,
    event_id: uuid.UUID,
    data: TimelineEventUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update timeline event."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.project_id == project_id
        )
    )
    evt = result.scalar_one_or_none()
    if not evt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(evt, k, v)
    await db.flush()
    await db.refresh(evt)
    return TimelineEventResponse.model_validate(evt)


@router.delete("/timeline/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_event(
    project_id: uuid.UUID,
    event_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete timeline event."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.project_id == project_id
        )
    )
    evt = result.scalar_one_or_none()
    if not evt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found")
    await db.delete(evt)


# --- Relationships ---

@router.get("/relationships", response_model=list[VaultRelationshipResponse])
async def list_relationships(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    character_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List relationships."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(VaultRelationship).where(VaultRelationship.project_id == project_id)
    if character_id is not None:
        stmt = stmt.where(
            (VaultRelationship.character_a_id == character_id)
            | (VaultRelationship.character_b_id == character_id)
        )
    result = await db.execute(stmt)
    rels = result.scalars().all()
    return [VaultRelationshipResponse.model_validate(r) for r in rels]


@router.post("/relationships", response_model=VaultRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    project_id: uuid.UUID,
    data: VaultRelationshipCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create relationship."""
    await _ensure_project_access(db, project_id, current_user.id)
    rel = VaultRelationship(
        project_id=project_id,
        character_a_id=data.character_a_id,
        character_b_id=data.character_b_id,
        relationship_type=data.relationship_type,
        description=data.description,
        status=data.status,
        history=data.history,
    )
    db.add(rel)
    await db.flush()
    await db.refresh(rel)
    return VaultRelationshipResponse.model_validate(rel)


@router.patch("/relationships/{rel_id}", response_model=VaultRelationshipResponse)
async def update_relationship(
    project_id: uuid.UUID,
    rel_id: uuid.UUID,
    data: VaultRelationshipUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update relationship."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultRelationship).where(
            VaultRelationship.id == rel_id, VaultRelationship.project_id == project_id
        )
    )
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rel, k, v)
    await db.flush()
    await db.refresh(rel)
    return VaultRelationshipResponse.model_validate(rel)


@router.delete("/relationships/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    project_id: uuid.UUID,
    rel_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete relationship."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(VaultRelationship).where(
            VaultRelationship.id == rel_id, VaultRelationship.project_id == project_id
        )
    )
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    await db.delete(rel)


# --- Themes ---

@router.get("/themes", response_model=list[ThemeResponse])
async def list_themes(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
    theme_type: str | None = Query(None),
    is_central: bool | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List themes."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(Theme).where(Theme.project_id == project_id)
    if book_id is not None:
        stmt = stmt.where(Theme.book_id == book_id)
    if theme_type:
        stmt = stmt.where(Theme.theme_type == theme_type)
    if is_central is not None:
        stmt = stmt.where(Theme.is_central == is_central)
    stmt = stmt.order_by(Theme.sort_order.asc(), Theme.name.asc()).limit(limit)
    result = await db.execute(stmt)
    themes = result.scalars().all()
    return [ThemeResponse.model_validate(t) for t in themes]


@router.post("/themes", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    project_id: uuid.UUID,
    data: ThemeCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create theme."""
    await _ensure_project_access(db, project_id, current_user.id)
    theme = Theme(
        project_id=project_id,
        name=data.name,
        theme_type=data.theme_type,
        description=data.description,
        notes=data.notes,
        is_central=data.is_central,
        book_id=data.book_id,
    )
    db.add(theme)
    await db.flush()
    await db.refresh(theme)
    return ThemeResponse.model_validate(theme)


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    project_id: uuid.UUID,
    theme_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get theme by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Theme).where(Theme.id == theme_id, Theme.project_id == project_id)
    )
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    return ThemeResponse.model_validate(theme)


@router.patch("/themes/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    project_id: uuid.UUID,
    theme_id: uuid.UUID,
    data: ThemeUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update theme."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Theme).where(Theme.id == theme_id, Theme.project_id == project_id)
    )
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(theme, k, v)
    await db.flush()
    await db.refresh(theme)
    return ThemeResponse.model_validate(theme)


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    project_id: uuid.UUID,
    theme_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete theme."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Theme).where(Theme.id == theme_id, Theme.project_id == project_id)
    )
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    await db.delete(theme)


# --- Sources ---

@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    source_type: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
):
    """List sources."""
    await _ensure_project_access(db, project_id, current_user.id)
    stmt = select(Source).where(Source.project_id == project_id)
    if source_type:
        stmt = stmt.where(Source.source_type == source_type)
    if status:
        stmt = stmt.where(Source.status == status)
    stmt = stmt.order_by(Source.sort_order.asc(), Source.title.asc()).limit(limit)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    return [SourceResponse.model_validate(s) for s in sources]


@router.post("/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    project_id: uuid.UUID,
    data: SourceCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create source."""
    await _ensure_project_access(db, project_id, current_user.id)
    src = Source(
        project_id=project_id,
        title=data.title,
        author=data.author,
        source_type=data.source_type,
        publication_date=data.publication_date,
        url=data.url,
        usage_notes=data.usage_notes,
        topic_tags=data.topic_tags or [],
        quote_extracts=data.quote_extracts or [],
        citation_notes=data.citation_notes,
        reliability_note=data.reliability_note,
        status=data.status,
    )
    db.add(src)
    await db.flush()
    await db.refresh(src)
    return SourceResponse.model_validate(src)


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    project_id: uuid.UUID,
    source_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get source by ID."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Source).where(Source.id == source_id, Source.project_id == project_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return SourceResponse.model_validate(src)


@router.patch("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    project_id: uuid.UUID,
    source_id: uuid.UUID,
    data: SourceUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update source."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Source).where(Source.id == source_id, Source.project_id == project_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(src, k, v)
    await db.flush()
    await db.refresh(src)
    return SourceResponse.model_validate(src)


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    project_id: uuid.UUID,
    source_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete source."""
    await _ensure_project_access(db, project_id, current_user.id)
    result = await db.execute(
        select(Source).where(Source.id == source_id, Source.project_id == project_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    await db.delete(src)


# --- Chapter Knowledge Panel ---

@router.get(
    "/books/{book_id}/chapters/{chapter_id}/knowledge",
    response_model=ChapterKnowledgePanel,
)
async def get_chapter_knowledge(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get chapter-linked knowledge panel: characters, locations, events, themes, sources, research."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    chapter = await get_chapter_or_404(db, book_id, chapter_id)

    chars: list[VaultCharacter] = []
    locs: list[VaultLocation] = []
    evts: list[TimelineEvent] = []
    themes_list: list[Theme] = []
    sources_list: list[Source] = []
    research_list: list[ResearchEntry] = []

    result = await db.execute(
        select(ChapterCharacterLink)
        .where(ChapterCharacterLink.chapter_id == chapter_id)
        .options(selectinload(ChapterCharacterLink.character))
    )
    links = result.scalars().all()
    chars = [l.character for l in links if l.character]

    result = await db.execute(
        select(ChapterLocationLink)
        .where(ChapterLocationLink.chapter_id == chapter_id)
        .options(selectinload(ChapterLocationLink.location))
    )
    links = result.scalars().all()
    locs = [l.location for l in links if l.location]

    result = await db.execute(
        select(ChapterEventLink)
        .where(ChapterEventLink.chapter_id == chapter_id)
        .options(selectinload(ChapterEventLink.event))
    )
    links = result.scalars().all()
    evts = [l.event for l in links if l.event]

    result = await db.execute(
        select(ChapterThemeLink)
        .where(ChapterThemeLink.chapter_id == chapter_id)
        .options(selectinload(ChapterThemeLink.theme))
    )
    links = result.scalars().all()
    themes_list = [l.theme for l in links if l.theme]

    result = await db.execute(
        select(ChapterSourceLink)
        .where(ChapterSourceLink.chapter_id == chapter_id)
        .options(selectinload(ChapterSourceLink.source))
    )
    links = result.scalars().all()
    sources_list = [l.source for l in links if l.source]

    result = await db.execute(
        select(ChapterResearchLink)
        .where(ChapterResearchLink.chapter_id == chapter_id)
        .options(selectinload(ChapterResearchLink.research_entry))
    )
    links = result.scalars().all()
    research_list = [l.research_entry for l in links if l.research_entry]

    return ChapterKnowledgePanel(
        chapter_id=chapter_id,
        characters=[VaultCharacterResponse.model_validate(c) for c in chars],
        locations=[VaultLocationResponse.model_validate(l) for l in locs],
        events=[TimelineEventResponse.model_validate(e) for e in evts],
        themes=[ThemeResponse.model_validate(t) for t in themes_list],
        sources=[SourceResponse.model_validate(s) for s in sources_list],
        research_entries=[ResearchEntryResponse.model_validate(r) for r in research_list],
    )


# --- Chapter link endpoints ---

@router.post(
    "/books/{book_id}/chapters/{chapter_id}/characters",
    response_model=ChapterCharacterLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_character_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterCharacterLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link character to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(VaultCharacter).where(
            VaultCharacter.id == data.character_id,
            VaultCharacter.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    link = ChapterCharacterLink(
        chapter_id=chapter_id,
        character_id=data.character_id,
        notes=data.notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterCharacterLinkResponse.model_validate(link)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/locations",
    response_model=ChapterLocationLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_location_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterLocationLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link location to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(VaultLocation).where(
            VaultLocation.id == data.location_id,
            VaultLocation.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    link = ChapterLocationLink(
        chapter_id=chapter_id,
        location_id=data.location_id,
        notes=data.notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterLocationLinkResponse.model_validate(link)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/events",
    response_model=ChapterEventLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_event_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterEventLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link timeline event to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == data.event_id,
            TimelineEvent.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    link = ChapterEventLink(
        chapter_id=chapter_id,
        event_id=data.event_id,
        notes=data.notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterEventLinkResponse.model_validate(link)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/themes",
    response_model=ChapterThemeLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_theme_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterThemeLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link theme to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(Theme).where(
            Theme.id == data.theme_id,
            Theme.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    link = ChapterThemeLink(
        chapter_id=chapter_id,
        theme_id=data.theme_id,
        notes=data.notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterThemeLinkResponse.model_validate(link)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/sources",
    response_model=ChapterSourceLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_source_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterSourceLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link source to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(Source).where(
            Source.id == data.source_id,
            Source.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    link = ChapterSourceLink(
        chapter_id=chapter_id,
        source_id=data.source_id,
        usage_notes=data.usage_notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterSourceLinkResponse.model_validate(link)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/research",
    response_model=ChapterResearchLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_research_to_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterResearchLinkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link research entry to chapter."""
    await _ensure_project_access(db, project_id, current_user.id)
    await get_book_in_project_or_404(db, book_id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(ResearchEntry).where(
            ResearchEntry.id == data.research_id,
            ResearchEntry.project_id == project_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    link = ChapterResearchLink(
        chapter_id=chapter_id,
        research_id=data.research_id,
        notes=data.notes,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return ChapterResearchLinkResponse.model_validate(link)
