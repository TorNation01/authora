"""Non-fiction workspace API routes."""

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
    ArgumentStructure,
    AuthorityBuilder,
    Book,
    CaseStudy,
    CitationPlaceholder,
    NFChapterPlan,
    NFResearchNote,
    NFWorksheet,
    NonfictionWorkspace,
    Project,
    StoryInsertion,
    SupportingExample,
    SummaryActionStep,
    TargetAudience,
    TransformationFramework,
)
from authora.schemas.nonfiction import (
    ArgumentStructureCreate,
    ArgumentStructureResponse,
    ArgumentStructureUpdate,
    AuthorityBuilderCreate,
    AuthorityBuilderResponse,
    AuthorityBuilderUpdate,
    CaseStudyCreate,
    CaseStudyResponse,
    CaseStudyUpdate,
    CitationPlaceholderCreate,
    CitationPlaceholderResponse,
    CitationPlaceholderUpdate,
    NFChapterPlanCreate,
    NFChapterPlanResponse,
    NFChapterPlanUpdate,
    NFResearchNoteCreate,
    NFResearchNoteResponse,
    NFResearchNoteUpdate,
    NFWorksheetCreate,
    NFWorksheetResponse,
    NFWorksheetUpdate,
    NonfictionWorkspaceCreate,
    NonfictionWorkspaceResponse,
    NonfictionWorkspaceUpdate,
    StoryInsertionCreate,
    StoryInsertionResponse,
    StoryInsertionUpdate,
    SupportingExampleCreate,
    SupportingExampleResponse,
    SupportingExampleUpdate,
    SummaryActionStepCreate,
    SummaryActionStepResponse,
    SummaryActionStepUpdate,
    TargetAudienceCreate,
    TargetAudienceResponse,
    TargetAudienceUpdate,
    TransformationFrameworkCreate,
    TransformationFrameworkResponse,
    TransformationFrameworkUpdate,
)

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}/nonfiction", tags=["nonfiction"])


async def get_nonfiction_book_or_404(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book:
    result = await db.execute(
        select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.type != "nonfiction":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not non-fiction")
    return book


async def get_workspace_or_create(db: AsyncSession, book_id: uuid.UUID) -> NonfictionWorkspace:
    result = await db.execute(select(NonfictionWorkspace).where(NonfictionWorkspace.book_id == book_id))
    ws = result.scalar_one_or_none()
    if not ws:
        ws = NonfictionWorkspace(book_id=book_id)
        db.add(ws)
        await db.flush()
        await db.refresh(ws)
    return ws


@router.get("/workspace", response_model=NonfictionWorkspaceResponse)
async def get_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    return await get_workspace_or_create(db, book_id)


@router.patch("/workspace", response_model=NonfictionWorkspaceResponse)
async def update_workspace(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: NonfictionWorkspaceUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    ws = await get_workspace_or_create(db, book_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(ws, k, v)
    await db.flush()
    await db.refresh(ws)
    return ws


# Target audiences
@router.get("/audiences", response_model=list[TargetAudienceResponse])
async def list_audiences(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TargetAudience).where(TargetAudience.book_id == book_id).order_by(TargetAudience.sort_order))
    return [TargetAudienceResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/audiences", response_model=TargetAudienceResponse, status_code=status.HTTP_201_CREATED)
async def create_audience(project_id: uuid.UUID, book_id: uuid.UUID, data: TargetAudienceCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = TargetAudience(book_id=book_id, demographics=data.demographics, pain_points=data.pain_points, goals=data.goals, objections=data.objections)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/audiences/{item_id}", response_model=TargetAudienceResponse)
async def update_audience(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: TargetAudienceUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TargetAudience).where(TargetAudience.id == item_id, TargetAudience.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/audiences/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audience(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TargetAudience).where(TargetAudience.id == item_id, TargetAudience.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Transformation frameworks
@router.get("/transformations", response_model=list[TransformationFrameworkResponse])
async def list_transformations(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TransformationFramework).where(TransformationFramework.book_id == book_id).order_by(TransformationFramework.sort_order))
    return [TransformationFrameworkResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/transformations", response_model=TransformationFrameworkResponse, status_code=status.HTTP_201_CREATED)
async def create_transformation(project_id: uuid.UUID, book_id: uuid.UUID, data: TransformationFrameworkCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = TransformationFramework(book_id=book_id, before_state=data.before_state, after_state=data.after_state, steps=data.steps)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/transformations/{item_id}", response_model=TransformationFrameworkResponse)
async def update_transformation(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: TransformationFrameworkUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TransformationFramework).where(TransformationFramework.id == item_id, TransformationFramework.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/transformations/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transformation(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(TransformationFramework).where(TransformationFramework.id == item_id, TransformationFramework.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Chapter plans
@router.get("/chapter-plans", response_model=list[NFChapterPlanResponse])
async def list_chapter_plans(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFChapterPlan).where(NFChapterPlan.book_id == book_id).order_by(NFChapterPlan.sort_order, NFChapterPlan.title))
    return [NFChapterPlanResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/chapter-plans", response_model=NFChapterPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter_plan(project_id: uuid.UUID, book_id: uuid.UUID, data: NFChapterPlanCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = NFChapterPlan(book_id=book_id, chapter_id=data.chapter_id, title=data.title, summary=data.summary, key_points=data.key_points)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/chapter-plans/{item_id}", response_model=NFChapterPlanResponse)
async def update_chapter_plan(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: NFChapterPlanUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFChapterPlan).where(NFChapterPlan.id == item_id, NFChapterPlan.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/chapter-plans/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter_plan(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFChapterPlan).where(NFChapterPlan.id == item_id, NFChapterPlan.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Arguments
@router.get("/arguments", response_model=list[ArgumentStructureResponse])
async def list_arguments(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(ArgumentStructure).where(ArgumentStructure.book_id == book_id).order_by(ArgumentStructure.sort_order))
    return [ArgumentStructureResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/arguments", response_model=ArgumentStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_argument(project_id: uuid.UUID, book_id: uuid.UUID, data: ArgumentStructureCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = ArgumentStructure(book_id=book_id, chapter_id=data.chapter_id, main_argument=data.main_argument, supporting_points=data.supporting_points)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/arguments/{item_id}", response_model=ArgumentStructureResponse)
async def update_argument(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: ArgumentStructureUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(ArgumentStructure).where(ArgumentStructure.id == item_id, ArgumentStructure.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/arguments/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_argument(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(ArgumentStructure).where(ArgumentStructure.id == item_id, ArgumentStructure.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Supporting examples
@router.get("/examples", response_model=list[SupportingExampleResponse])
async def list_examples(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SupportingExample).where(SupportingExample.book_id == book_id).order_by(SupportingExample.sort_order, SupportingExample.title))
    return [SupportingExampleResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/examples", response_model=SupportingExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(project_id: uuid.UUID, book_id: uuid.UUID, data: SupportingExampleCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = SupportingExample(book_id=book_id, chapter_id=data.chapter_id, title=data.title, description=data.description, category=data.category)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/examples/{item_id}", response_model=SupportingExampleResponse)
async def update_example(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: SupportingExampleUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SupportingExample).where(SupportingExample.id == item_id, SupportingExample.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/examples/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SupportingExample).where(SupportingExample.id == item_id, SupportingExample.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Case studies
@router.get("/case-studies", response_model=list[CaseStudyResponse])
async def list_case_studies(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CaseStudy).where(CaseStudy.book_id == book_id).order_by(CaseStudy.sort_order, CaseStudy.title))
    return [CaseStudyResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/case-studies", response_model=CaseStudyResponse, status_code=status.HTTP_201_CREATED)
async def create_case_study(project_id: uuid.UUID, book_id: uuid.UUID, data: CaseStudyCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = CaseStudy(book_id=book_id, chapter_id=data.chapter_id, title=data.title, scenario=data.scenario, outcome=data.outcome, lessons=data.lessons)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/case-studies/{item_id}", response_model=CaseStudyResponse)
async def update_case_study(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: CaseStudyUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CaseStudy).where(CaseStudy.id == item_id, CaseStudy.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/case-studies/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case_study(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CaseStudy).where(CaseStudy.id == item_id, CaseStudy.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Story insertions
@router.get("/story-insertions", response_model=list[StoryInsertionResponse])
async def list_story_insertions(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(StoryInsertion).where(StoryInsertion.book_id == book_id).order_by(StoryInsertion.sort_order))
    return [StoryInsertionResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/story-insertions", response_model=StoryInsertionResponse, status_code=status.HTTP_201_CREATED)
async def create_story_insertion(project_id: uuid.UUID, book_id: uuid.UUID, data: StoryInsertionCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = StoryInsertion(book_id=book_id, chapter_id=data.chapter_id, story_content=data.story_content, purpose=data.purpose, placement_notes=data.placement_notes)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/story-insertions/{item_id}", response_model=StoryInsertionResponse)
async def update_story_insertion(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: StoryInsertionUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(StoryInsertion).where(StoryInsertion.id == item_id, StoryInsertion.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/story-insertions/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story_insertion(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(StoryInsertion).where(StoryInsertion.id == item_id, StoryInsertion.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Worksheets
@router.get("/worksheets", response_model=list[NFWorksheetResponse])
async def list_worksheets(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFWorksheet).where(NFWorksheet.book_id == book_id).order_by(NFWorksheet.sort_order, NFWorksheet.title))
    return [NFWorksheetResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/worksheets", response_model=NFWorksheetResponse, status_code=status.HTTP_201_CREATED)
async def create_worksheet(project_id: uuid.UUID, book_id: uuid.UUID, data: NFWorksheetCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = NFWorksheet(book_id=book_id, chapter_id=data.chapter_id, title=data.title, items=data.items)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/worksheets/{item_id}", response_model=NFWorksheetResponse)
async def update_worksheet(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: NFWorksheetUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFWorksheet).where(NFWorksheet.id == item_id, NFWorksheet.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/worksheets/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worksheet(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFWorksheet).where(NFWorksheet.id == item_id, NFWorksheet.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Research notes
@router.get("/research-notes", response_model=list[NFResearchNoteResponse])
async def list_research_notes(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFResearchNote).where(NFResearchNote.book_id == book_id).order_by(NFResearchNote.sort_order, NFResearchNote.title))
    return [NFResearchNoteResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/research-notes", response_model=NFResearchNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_research_note(project_id: uuid.UUID, book_id: uuid.UUID, data: NFResearchNoteCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = NFResearchNote(book_id=book_id, chapter_id=data.chapter_id, title=data.title, content=data.content, source=data.source)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/research-notes/{item_id}", response_model=NFResearchNoteResponse)
async def update_research_note(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: NFResearchNoteUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFResearchNote).where(NFResearchNote.id == item_id, NFResearchNote.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/research-notes/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_note(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(NFResearchNote).where(NFResearchNote.id == item_id, NFResearchNote.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Citations
@router.get("/citations", response_model=list[CitationPlaceholderResponse])
async def list_citations(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CitationPlaceholder).where(CitationPlaceholder.book_id == book_id).order_by(CitationPlaceholder.sort_order))
    return [CitationPlaceholderResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/citations", response_model=CitationPlaceholderResponse, status_code=status.HTTP_201_CREATED)
async def create_citation(project_id: uuid.UUID, book_id: uuid.UUID, data: CitationPlaceholderCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = CitationPlaceholder(book_id=book_id, chapter_id=data.chapter_id, placeholder_text=data.placeholder_text, source_hint=data.source_hint)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/citations/{item_id}", response_model=CitationPlaceholderResponse)
async def update_citation(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: CitationPlaceholderUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CitationPlaceholder).where(CitationPlaceholder.id == item_id, CitationPlaceholder.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/citations/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_citation(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(CitationPlaceholder).where(CitationPlaceholder.id == item_id, CitationPlaceholder.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Authority
@router.get("/authority", response_model=list[AuthorityBuilderResponse])
async def list_authority(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(AuthorityBuilder).where(AuthorityBuilder.book_id == book_id).order_by(AuthorityBuilder.sort_order))
    return [AuthorityBuilderResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/authority", response_model=AuthorityBuilderResponse, status_code=status.HTTP_201_CREATED)
async def create_authority(project_id: uuid.UUID, book_id: uuid.UUID, data: AuthorityBuilderCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = AuthorityBuilder(book_id=book_id, credentials=data.credentials, experience=data.experience, testimonials=data.testimonials)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/authority/{item_id}", response_model=AuthorityBuilderResponse)
async def update_authority(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: AuthorityBuilderUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(AuthorityBuilder).where(AuthorityBuilder.id == item_id, AuthorityBuilder.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/authority/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_authority(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(AuthorityBuilder).where(AuthorityBuilder.id == item_id, AuthorityBuilder.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Summary/action steps
@router.get("/summary-actions", response_model=list[SummaryActionStepResponse])
async def list_summary_actions(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SummaryActionStep).where(SummaryActionStep.book_id == book_id).order_by(SummaryActionStep.sort_order))
    return [SummaryActionStepResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/summary-actions", response_model=SummaryActionStepResponse, status_code=status.HTTP_201_CREATED)
async def create_summary_action(project_id: uuid.UUID, book_id: uuid.UUID, data: SummaryActionStepCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    r = SummaryActionStep(book_id=book_id, chapter_id=data.chapter_id, summary=data.summary, action_steps=data.action_steps)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return r


@router.patch("/summary-actions/{item_id}", response_model=SummaryActionStepResponse)
async def update_summary_action(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, data: SummaryActionStepUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SummaryActionStep).where(SummaryActionStep.id == item_id, SummaryActionStep.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    return r


@router.delete("/summary-actions/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary_action(project_id: uuid.UUID, book_id: uuid.UUID, item_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    result = await db.execute(select(SummaryActionStep).where(SummaryActionStep.id == item_id, SummaryActionStep.book_id == book_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(r)


# Summary endpoint
@router.get("/summary")
async def get_summary(project_id: uuid.UUID, book_id: uuid.UUID, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    ws = await get_workspace_or_create(db, book_id)

    async def _fetch(Model, order):
        r = await db.execute(select(Model).where(Model.book_id == book_id).order_by(*order))
        return r.scalars().all()

    audiences = await _fetch(TargetAudience, [TargetAudience.sort_order])
    transformations = await _fetch(TransformationFramework, [TransformationFramework.sort_order])
    chapter_plans = await _fetch(NFChapterPlan, [NFChapterPlan.sort_order, NFChapterPlan.title])
    arguments = await _fetch(ArgumentStructure, [ArgumentStructure.sort_order])
    examples = await _fetch(SupportingExample, [SupportingExample.sort_order, SupportingExample.title])
    case_studies = await _fetch(CaseStudy, [CaseStudy.sort_order, CaseStudy.title])
    story_insertions = await _fetch(StoryInsertion, [StoryInsertion.sort_order])
    worksheets = await _fetch(NFWorksheet, [NFWorksheet.sort_order, NFWorksheet.title])
    research_notes = await _fetch(NFResearchNote, [NFResearchNote.sort_order, NFResearchNote.title])
    citations = await _fetch(CitationPlaceholder, [CitationPlaceholder.sort_order])
    authority = await _fetch(AuthorityBuilder, [AuthorityBuilder.sort_order])
    summary_actions = await _fetch(SummaryActionStep, [SummaryActionStep.sort_order])

    return {
        "workspace": NonfictionWorkspaceResponse.model_validate(ws),
        "audiences": [TargetAudienceResponse.model_validate(a) for a in audiences],
        "transformations": [TransformationFrameworkResponse.model_validate(t) for t in transformations],
        "chapter_plans": [NFChapterPlanResponse.model_validate(c) for c in chapter_plans],
        "arguments": [ArgumentStructureResponse.model_validate(a) for a in arguments],
        "examples": [SupportingExampleResponse.model_validate(e) for e in examples],
        "case_studies": [CaseStudyResponse.model_validate(c) for c in case_studies],
        "story_insertions": [StoryInsertionResponse.model_validate(s) for s in story_insertions],
        "worksheets": [NFWorksheetResponse.model_validate(w) for w in worksheets],
        "research_notes": [NFResearchNoteResponse.model_validate(r) for r in research_notes],
        "citations": [CitationPlaceholderResponse.model_validate(c) for c in citations],
        "authority": [AuthorityBuilderResponse.model_validate(a) for a in authority],
        "summary_actions": [SummaryActionStepResponse.model_validate(s) for s in summary_actions],
    }


# Nonfiction AI
class NonfictionAIRequest(BaseModel):
    prompt_type: str
    context: str | None = None
    chapter_id: uuid.UUID | None = None
    selection: str | None = None


@router.post("/ai")
async def nonfiction_ai_stream(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: NonfictionAIRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    from authora.config import get_settings
    from authora.services.nonfiction_ai import NONFICTION_PROMPT_TEMPLATES, build_nonfiction_context
    from authora.services.ai import complete

    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    await get_nonfiction_book_or_404(db, book_id, current_user.id)
    system = await build_nonfiction_context(db, book_id, data.chapter_id, include_recent=bool(data.chapter_id))

    template = NONFICTION_PROMPT_TEMPLATES.get(data.prompt_type)
    if not template:
        raise HTTPException(status_code=400, detail=f"Unknown prompt type: {data.prompt_type}")

    format_kw = {"selection": data.selection or "", "context": data.context or ""}
    try:
        user_prompt = template.format(**format_kw)
    except KeyError:
        user_prompt = template
    if data.context and "{context}" not in template and "{selection}" not in template:
        user_prompt = f"{user_prompt}\n\n{data.context}"

    async def generate():
        async for chunk in complete(user_prompt, system, 2048):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
