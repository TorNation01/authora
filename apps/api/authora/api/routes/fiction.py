"""Fiction workspace API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import (
    Book,
    CharacterRelationship,
    FictionCharacter,
    FictionChapterPlan,
    FictionTracker,
    FictionWorkspace,
    PlotArc,
    Project,
    Scene,
    WorldElement,
)
from authora.services.fiction_ai import build_fiction_context
from authora.services.ai import complete
from authora.schemas.fiction import (
    CharacterRelationshipCreate,
    CharacterRelationshipResponse,
    CharacterRelationshipUpdate,
    FictionChapterPlanCreate,
    FictionChapterPlanResponse,
    FictionChapterPlanUpdate,
    FictionCharacterCreate,
    FictionCharacterResponse,
    FictionCharacterUpdate,
    FictionTrackerCreate,
    FictionTrackerResponse,
    FictionTrackerUpdate,
    FictionWorkspaceCreate,
    FictionWorkspaceResponse,
    FictionWorkspaceUpdate,
    PlotArcCreate,
    PlotArcResponse,
    PlotArcUpdate,
    SceneCreate,
    SceneResponse,
    SceneUpdate,
    WorldElementCreate,
    WorldElementResponse,
    WorldElementUpdate,
)

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}/fiction", tags=["fiction"])


async def get_fiction_book_or_404(
    db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID
) -> Book:
    result = await db.execute(
        select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.type != "fiction":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not fiction")
    return book


async def get_workspace_or_create(
    db: AsyncSession, book_id: uuid.UUID
) -> FictionWorkspace:
    result = await db.execute(select(FictionWorkspace).where(FictionWorkspace.book_id == book_id))
    ws = result.scalar_one_or_none()
    if not ws:
        ws = FictionWorkspace(book_id=book_id)
        db.add(ws)
        await db.flush()
        await db.refresh(ws)
    return ws


@router.get("/workspace", response_model=FictionWorkspaceResponse)
async def get_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get or create fiction workspace."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    return await get_workspace_or_create(db, book_id)


@router.patch("/workspace", response_model=FictionWorkspaceResponse)
async def update_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionWorkspaceUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update fiction workspace."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    ws = await get_workspace_or_create(db, book_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(ws, k, v)
    await db.flush()
    await db.refresh(ws)
    return ws


@router.post("/workspace", response_model=FictionWorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionWorkspaceCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create fiction workspace."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(FictionWorkspace).where(FictionWorkspace.book_id == book_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace already exists")
    ws = FictionWorkspace(
        book_id=book_id,
        premise=data.premise,
        genre=data.genre,
        tone=data.tone,
        themes=data.themes,
        pacing_notes=data.pacing_notes,
    )
    db.add(ws)
    await db.flush()
    await db.refresh(ws)
    return ws


# Characters
@router.get("/characters", response_model=list[FictionCharacterResponse])
async def list_characters(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List characters."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionCharacter).where(FictionCharacter.book_id == book_id).order_by(FictionCharacter.sort_order, FictionCharacter.name)
    )
    return [FictionCharacterResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/characters", response_model=FictionCharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionCharacterCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create character."""
    book = await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(FictionCharacter).where(FictionCharacter.book_id == book_id))
    sort_order = len(result.scalars().all())
    char = FictionCharacter(
        book_id=book_id,
        name=data.name,
        role=data.role,
        description=data.description,
        backstory=data.backstory,
        goals=data.goals,
        flaws=data.flaws,
        traits=data.traits,
        sort_order=sort_order,
    )
    db.add(char)
    await db.flush()
    await db.refresh(char)
    return char


@router.patch("/characters/{character_id}", response_model=FictionCharacterResponse)
async def update_character(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    character_id: uuid.UUID,
    data: FictionCharacterUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update character."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionCharacter).where(FictionCharacter.id == character_id, FictionCharacter.book_id == book_id)
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(char, k, v)
    await db.flush()
    await db.refresh(char)
    return char


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete character."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionCharacter).where(FictionCharacter.id == character_id, FictionCharacter.book_id == book_id)
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    await db.delete(char)


# Relationships
@router.get("/relationships", response_model=list[CharacterRelationshipResponse])
async def list_relationships(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List character relationships."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(CharacterRelationship).where(CharacterRelationship.book_id == book_id)
    )
    return [CharacterRelationshipResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/relationships", response_model=CharacterRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: CharacterRelationshipCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create relationship."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    rel = CharacterRelationship(
        book_id=book_id,
        character_a_id=data.character_a_id,
        character_b_id=data.character_b_id,
        relationship_type=data.relationship_type,
        description=data.description,
        arc_notes=data.arc_notes,
    )
    db.add(rel)
    await db.flush()
    await db.refresh(rel)
    return rel


@router.patch("/relationships/{relationship_id}", response_model=CharacterRelationshipResponse)
async def update_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    relationship_id: uuid.UUID,
    data: CharacterRelationshipUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update relationship."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(CharacterRelationship).where(
            CharacterRelationship.id == relationship_id,
            CharacterRelationship.book_id == book_id,
        )
    )
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rel, k, v)
    await db.flush()
    await db.refresh(rel)
    return rel


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    relationship_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete relationship."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(CharacterRelationship).where(
            CharacterRelationship.id == relationship_id,
            CharacterRelationship.book_id == book_id,
        )
    )
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    await db.delete(rel)


# World elements
@router.get("/world", response_model=list[WorldElementResponse])
async def list_world_elements(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List world elements."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(WorldElement).where(WorldElement.book_id == book_id).order_by(WorldElement.sort_order, WorldElement.name)
    )
    return [WorldElementResponse.model_validate(w) for w in result.scalars().all()]


@router.post("/world", response_model=WorldElementResponse, status_code=status.HTTP_201_CREATED)
async def create_world_element(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: WorldElementCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create world element."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(WorldElement).where(WorldElement.book_id == book_id))
    sort_order = len(result.scalars().all())
    el = WorldElement(
        book_id=book_id,
        name=data.name,
        category=data.category,
        description=data.description,
        details=data.details,
        sort_order=sort_order,
    )
    db.add(el)
    await db.flush()
    await db.refresh(el)
    return el


@router.patch("/world/{element_id}", response_model=WorldElementResponse)
async def update_world_element(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    element_id: uuid.UUID,
    data: WorldElementUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update world element."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(WorldElement).where(WorldElement.id == element_id, WorldElement.book_id == book_id)
    )
    el = result.scalar_one_or_none()
    if not el:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World element not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(el, k, v)
    await db.flush()
    await db.refresh(el)
    return el


@router.delete("/world/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_element(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    element_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete world element."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(WorldElement).where(WorldElement.id == element_id, WorldElement.book_id == book_id)
    )
    el = result.scalar_one_or_none()
    if not el:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World element not found")
    await db.delete(el)


# Plot arcs
@router.get("/arcs", response_model=list[PlotArcResponse])
async def list_plot_arcs(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List plot arcs."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(PlotArc).where(PlotArc.book_id == book_id).order_by(PlotArc.sort_order, PlotArc.name)
    )
    return [PlotArcResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/arcs", response_model=PlotArcResponse, status_code=status.HTTP_201_CREATED)
async def create_plot_arc(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: PlotArcCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create plot arc."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    arc = PlotArc(
        book_id=book_id,
        name=data.name,
        structure=data.structure,
        beats=data.beats,
    )
    db.add(arc)
    await db.flush()
    await db.refresh(arc)
    return arc


@router.patch("/arcs/{arc_id}", response_model=PlotArcResponse)
async def update_plot_arc(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    arc_id: uuid.UUID,
    data: PlotArcUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update plot arc."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(PlotArc).where(PlotArc.id == arc_id, PlotArc.book_id == book_id)
    )
    arc = result.scalar_one_or_none()
    if not arc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot arc not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(arc, k, v)
    await db.flush()
    await db.refresh(arc)
    return arc


@router.delete("/arcs/{arc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot_arc(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    arc_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete plot arc."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(PlotArc).where(PlotArc.id == arc_id, PlotArc.book_id == book_id)
    )
    arc = result.scalar_one_or_none()
    if not arc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot arc not found")
    await db.delete(arc)


# Scenes
@router.get("/scenes", response_model=list[SceneResponse])
async def list_scenes(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID | None = None,
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """List scenes, optionally filtered by chapter."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    q = select(Scene).where(Scene.book_id == book_id)
    if chapter_id:
        q = q.where(Scene.chapter_id == chapter_id)
    q = q.order_by(Scene.sort_order, Scene.title)
    result = await db.execute(q)
    return [SceneResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/scenes", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
async def create_scene(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: SceneCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create scene."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(Scene).where(Scene.book_id == book_id))
    sort_order = len(result.scalars().all())
    scene = Scene(
        book_id=book_id,
        chapter_id=data.chapter_id,
        pov_character_id=data.pov_character_id,
        title=data.title,
        summary=data.summary,
        beat=data.beat,
        conflict_level=data.conflict_level,
        escalation_notes=data.escalation_notes,
        sort_order=sort_order,
    )
    db.add(scene)
    await db.flush()
    await db.refresh(scene)
    return scene


@router.patch("/scenes/{scene_id}", response_model=SceneResponse)
async def update_scene(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    scene_id: uuid.UUID,
    data: SceneUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update scene."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(Scene).where(Scene.id == scene_id, Scene.book_id == book_id)
    )
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(scene, k, v)
    await db.flush()
    await db.refresh(scene)
    return scene


@router.delete("/scenes/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scene(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    scene_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete scene."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(Scene).where(Scene.id == scene_id, Scene.book_id == book_id)
    )
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
    await db.delete(scene)


# Trackers
@router.get("/trackers", response_model=list[FictionTrackerResponse])
async def list_trackers(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tracker_type: str | None = None,
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """List trackers (continuity, foreshadowing, unresolved)."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    q = select(FictionTracker).where(FictionTracker.book_id == book_id)
    if tracker_type:
        q = q.where(FictionTracker.type == tracker_type)
    q = q.order_by(FictionTracker.sort_order, FictionTracker.title)
    result = await db.execute(q)
    return [FictionTrackerResponse.model_validate(t) for t in result.scalars().all()]


@router.post("/trackers", response_model=FictionTrackerResponse, status_code=status.HTTP_201_CREATED)
async def create_tracker(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionTrackerCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create tracker."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(FictionTracker).where(FictionTracker.book_id == book_id))
    sort_order = len(result.scalars().all())
    tracker = FictionTracker(
        book_id=book_id,
        chapter_id=data.chapter_id,
        type=data.type,
        title=data.title,
        content=data.content,
        target_chapter_id=data.target_chapter_id,
        sort_order=sort_order,
    )
    db.add(tracker)
    await db.flush()
    await db.refresh(tracker)
    return tracker


@router.patch("/trackers/{tracker_id}", response_model=FictionTrackerResponse)
async def update_tracker(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tracker_id: uuid.UUID,
    data: FictionTrackerUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update tracker."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionTracker).where(
            FictionTracker.id == tracker_id,
            FictionTracker.book_id == book_id,
        )
    )
    tracker = result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracker not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(tracker, k, v)
    await db.flush()
    await db.refresh(tracker)
    return tracker


@router.delete("/trackers/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracker(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    tracker_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete tracker."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionTracker).where(
            FictionTracker.id == tracker_id,
            FictionTracker.book_id == book_id,
        )
    )
    tracker = result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracker not found")
    await db.delete(tracker)


# Chapter plans
@router.get("/chapter-plans", response_model=list[FictionChapterPlanResponse])
async def list_chapter_plans(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List chapter plans."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionChapterPlan).where(FictionChapterPlan.book_id == book_id).order_by(FictionChapterPlan.sort_order, FictionChapterPlan.title)
    )
    return [FictionChapterPlanResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/chapter-plans", response_model=FictionChapterPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter_plan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionChapterPlanCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create chapter plan."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(FictionChapterPlan).where(FictionChapterPlan.book_id == book_id))
    sort_order = len(result.scalars().all())
    plan = FictionChapterPlan(
        book_id=book_id,
        chapter_id=data.chapter_id,
        title=data.title,
        summary=data.summary,
        goals=data.goals,
        conflicts=data.conflicts,
        scene_ids=data.scene_ids,
        sort_order=sort_order,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.patch("/chapter-plans/{plan_id}", response_model=FictionChapterPlanResponse)
async def update_chapter_plan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    plan_id: uuid.UUID,
    data: FictionChapterPlanUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update chapter plan."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionChapterPlan).where(
            FictionChapterPlan.id == plan_id,
            FictionChapterPlan.book_id == book_id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter plan not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.delete("/chapter-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter_plan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete chapter plan."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(
        select(FictionChapterPlan).where(
            FictionChapterPlan.id == plan_id,
            FictionChapterPlan.book_id == book_id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter plan not found")
    await db.delete(plan)


# Full workspace summary
@router.get("/summary")
async def get_workspace_summary(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get full fiction workspace for AI context and UI."""
    await get_fiction_book_or_404(db, book_id, current_user.id)
    ws = await get_workspace_or_create(db, book_id)

    chars = (await db.execute(select(FictionCharacter).where(FictionCharacter.book_id == book_id).order_by(FictionCharacter.sort_order))).scalars().all()
    rels = (await db.execute(select(CharacterRelationship).where(CharacterRelationship.book_id == book_id))).scalars().all()
    world = (await db.execute(select(WorldElement).where(WorldElement.book_id == book_id).order_by(WorldElement.sort_order))).scalars().all()
    arcs = (await db.execute(select(PlotArc).where(PlotArc.book_id == book_id).order_by(PlotArc.sort_order))).scalars().all()
    scenes = (await db.execute(select(Scene).where(Scene.book_id == book_id).order_by(Scene.sort_order))).scalars().all()
    trackers = (await db.execute(select(FictionTracker).where(FictionTracker.book_id == book_id).order_by(FictionTracker.sort_order))).scalars().all()
    plans = (await db.execute(select(FictionChapterPlan).where(FictionChapterPlan.book_id == book_id).order_by(FictionChapterPlan.sort_order))).scalars().all()

    return {
        "workspace": FictionWorkspaceResponse.model_validate(ws),
        "characters": [FictionCharacterResponse.model_validate(c) for c in chars],
        "relationships": [CharacterRelationshipResponse.model_validate(r) for r in rels],
        "world_elements": [WorldElementResponse.model_validate(w) for w in world],
        "plot_arcs": [PlotArcResponse.model_validate(a) for a in arcs],
        "scenes": [SceneResponse.model_validate(s) for s in scenes],
        "trackers": [FictionTrackerResponse.model_validate(t) for t in trackers],
        "chapter_plans": [FictionChapterPlanResponse.model_validate(p) for p in plans],
    }


# Fiction AI - streaming
class FictionAIRequest(BaseModel):
    prompt_type: str
    context: str | None = None
    chapter_id: uuid.UUID | None = None
    scene_id: uuid.UUID | None = None
    selection: str | None = None


@router.post("/ai")
async def fiction_ai_stream(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: FictionAIRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Stream AI response for fiction-specific prompts."""
    from authora.config import get_settings
    from authora.services.fiction_ai import FICTION_PROMPT_TEMPLATES

    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    await get_fiction_book_or_404(db, book_id, current_user.id)
    system = await build_fiction_context(
        db, book_id, data.chapter_id, data.scene_id, include_recent=bool(data.chapter_id)
    )

    template = FICTION_PROMPT_TEMPLATES.get(data.prompt_type)
    if not template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown prompt type: {data.prompt_type}")

    format_kw = {
        "selection": data.selection or "",
        "pov": "another character's",
        "characters": "the main characters",
        "context": data.context or "",
    }
    try:
        user_prompt = template.format(**format_kw)
    except KeyError:
        user_prompt = template
    if data.context and "{context}" not in template and "{selection}" not in template:
        user_prompt = f"{user_prompt}\n\n{data.context}"

    async def generate():
        async for chunk in complete(user_prompt, system, 2048):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
