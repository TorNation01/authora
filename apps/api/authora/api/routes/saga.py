"""Saga API - the tier above the series.

A saga owns the enduring truths of a whole multi-series undertaking. Below it
sit series plans (one per constituent series or major phase) and, below those,
the ordinary projects that already exist. Two ledgers run alongside: promises
made to the reader, and truths with their reveal points.

Everything here is additive. A project joins a saga by carrying ``saga_id``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_project_or_404
from authora.data.saga_schema import (
    BOOK_CONNECTION_SECTIONS,
    SAGA_OUTLINE_SECTIONS,
    SAGA_SECTIONS,
    SERIES_PLAN_SECTIONS,
    blank_sections,
    completeness,
    merge_sections,
)
from authora.database import get_db
from authora.models import Book, Project, Saga, SagaOutline, SagaThread, SagaTruth, SeriesPlan

router = APIRouter(prefix="/sagas", tags=["saga"])

Db = Annotated[AsyncSession, Depends(get_db)]


# --------------------------------------------------------------------------
# Payloads
# --------------------------------------------------------------------------


class SagaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sections: dict[str, Any] = Field(default_factory=dict)


class SagaUpdate(BaseModel):
    name: str | None = None
    sections: dict[str, Any] | None = None
    section_status: dict[str, str] | None = None


class OutlineUpdate(BaseModel):
    sections: dict[str, Any] = Field(default_factory=dict)


class SeriesPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    kind: str = "series"
    position: int | None = None
    sections: dict[str, Any] = Field(default_factory=dict)


class SeriesPlanUpdate(BaseModel):
    name: str | None = None
    kind: str | None = None
    position: int | None = None
    sections: dict[str, Any] | None = None
    section_status: dict[str, str] | None = None


class ThreadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    detail: str | None = None
    status: str = "open"
    opened_in: str | None = None
    paid_in: str | None = None
    notes: str | None = None
    sort_order: int = 0


class ThreadUpdate(BaseModel):
    name: str | None = None
    detail: str | None = None
    status: str | None = None
    opened_in: str | None = None
    paid_in: str | None = None
    notes: str | None = None
    sort_order: int | None = None


class TruthCreate(BaseModel):
    statement: str = Field(min_length=1)
    level: str = "saga"
    status: str = "hidden"
    knows: list[str] = Field(default_factory=list)
    believes_otherwise: list[str] = Field(default_factory=list)
    reveal_point: str | None = None
    notes: str | None = None
    sort_order: int = 0


class TruthUpdate(BaseModel):
    statement: str | None = None
    level: str | None = None
    status: str | None = None
    knows: list[str] | None = None
    believes_otherwise: list[str] | None = None
    reveal_point: str | None = None
    notes: str | None = None
    sort_order: int | None = None


class LinkProject(BaseModel):
    project_id: uuid.UUID


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


async def get_saga_or_404(db: AsyncSession, saga_id: uuid.UUID, user_id: uuid.UUID) -> Saga:
    result = await db.execute(
        select(Saga).where(Saga.id == saga_id, Saga.user_id == user_id, Saga.deleted_at.is_(None))
    )
    saga = result.scalar_one_or_none()
    if saga is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saga not found")
    return saga


async def get_or_create_outline(db: AsyncSession, saga_id: uuid.UUID) -> SagaOutline:
    result = await db.execute(select(SagaOutline).where(SagaOutline.saga_id == saga_id))
    outline = result.scalar_one_or_none()
    if outline is None:
        outline = SagaOutline(saga_id=saga_id, sections=blank_sections(SAGA_OUTLINE_SECTIONS))
        db.add(outline)
        await db.commit()
        await db.refresh(outline)
    return outline


async def thread_counts(db: AsyncSession, saga_id: uuid.UUID) -> dict[str, int]:
    result = await db.execute(
        select(SagaThread.status, func.count()).where(SagaThread.saga_id == saga_id).group_by(SagaThread.status)
    )
    return {row[0]: int(row[1]) for row in result.all()}


async def truth_counts(db: AsyncSession, saga_id: uuid.UUID) -> dict[str, int]:
    result = await db.execute(
        select(SagaTruth.status, func.count()).where(SagaTruth.saga_id == saga_id).group_by(SagaTruth.status)
    )
    return {row[0]: int(row[1]) for row in result.all()}


async def linked_projects(db: AsyncSession, saga_id: uuid.UUID) -> list[dict[str, Any]]:
    rows = await db.execute(
        select(Project, func.count(Book.id))
        .outerjoin(Book, Book.project_id == Project.id)
        .where(Project.saga_id == saga_id)
        .group_by(Project.id)
        .order_by(Project.created_at.asc())
    )
    out: list[dict[str, Any]] = []
    for project, book_count in rows.all():
        out.append(
            {
                "id": str(project.id),
                "name": project.name,
                "title": project.name,
                "scope": getattr(project, "scope", "series"),
                "book_count": int(book_count or 0),
            }
        )
    return out


def saga_summary(saga: Saga) -> dict[str, Any]:
    data = saga.sections or {}
    name = saga.name
    return {
        "id": str(saga.id),
        "name": name,
        "version": saga.version,
        "updated_at": saga.updated_at.isoformat() if saga.updated_at else None,
        "completeness": completeness(data, SAGA_SECTIONS),
    }


# --------------------------------------------------------------------------
# Schema + collection
# --------------------------------------------------------------------------


@router.get("/schema")
async def get_schema() -> dict[str, Any]:
    return {
        "sections": SAGA_SECTIONS,
        "outline_sections": SAGA_OUTLINE_SECTIONS,
        "series_sections": SERIES_PLAN_SECTIONS,
        "connection_sections": BOOK_CONNECTION_SECTIONS,
        "thread_statuses": ["open", "developing", "paid", "dropped"],
        "truth_statuses": ["hidden", "clued", "revealed"],
        "truth_levels": ["saga", "series", "book"],
        "scopes": ["standalone", "series"],
    }


@router.get("")
async def list_sagas(db: Db, user: CurrentUser) -> dict[str, Any]:
    result = await db.execute(
        select(Saga)
        .where(Saga.user_id == user.id, Saga.deleted_at.is_(None))
        .order_by(Saga.updated_at.desc())
    )
    sagas = result.scalars().all()
    items = []
    for saga in sagas:
        summary = saga_summary(saga)
        summary["projects"] = await linked_projects(db, saga.id)
        summary["threads"] = await thread_counts(db, saga.id)
        summary["truths"] = await truth_counts(db, saga.id)
        items.append(summary)
    return {"sagas": items, "count": len(items)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_saga(payload: SagaCreate, db: Db, user: CurrentUser) -> dict[str, Any]:
    sections = merge_sections(blank_sections(), payload.sections)
    saga = Saga(user_id=user.id, name=payload.name, sections=sections, section_status={})
    db.add(saga)
    await db.commit()
    await db.refresh(saga)
    return {"saga": saga_summary(saga), "sections": saga.sections}


# --------------------------------------------------------------------------
# One saga
# --------------------------------------------------------------------------


@router.get("/{saga_id}")
async def read_saga(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    saga = await get_saga_or_404(db, saga_id, user.id)
    outline = await get_or_create_outline(db, saga_id)
    return {
        "saga": saga_summary(saga),
        "sections": saga.sections,
        "section_status": saga.section_status,
        "outline": {
            "id": str(outline.id),
            "sections": outline.sections,
            "version": outline.version,
            "completeness": completeness(outline.sections or {}, SAGA_OUTLINE_SECTIONS),
        },
        "projects": await linked_projects(db, saga_id),
        "threads": await thread_counts(db, saga_id),
        "truths": await truth_counts(db, saga_id),
    }


@router.patch("/{saga_id}")
async def update_saga(saga_id: uuid.UUID, payload: SagaUpdate, db: Db, user: CurrentUser) -> dict[str, Any]:
    saga = await get_saga_or_404(db, saga_id, user.id)
    if payload.name:
        saga.name = payload.name
    if payload.sections is not None:
        saga.sections = merge_sections(saga.sections or blank_sections(), payload.sections)
        saga.version = (saga.version or 0) + 1
    if payload.section_status is not None:
        merged_status = dict(saga.section_status or {})
        merged_status.update(payload.section_status)
        saga.section_status = merged_status
    await db.commit()
    await db.refresh(saga)
    return {"saga": saga_summary(saga), "sections": saga.sections}


@router.delete("/{saga_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saga(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> None:
    saga = await get_saga_or_404(db, saga_id, user.id)
    saga.deleted_at = datetime.utcnow()
    projects = await db.execute(select(Project).where(Project.saga_id == saga_id))
    for project in projects.scalars().all():
        project.saga_id = None
    await db.commit()


# --------------------------------------------------------------------------
# Outline
# --------------------------------------------------------------------------


@router.get("/{saga_id}/outline")
async def read_outline(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    outline = await get_or_create_outline(db, saga_id)
    return {
        "saga_id": str(saga_id),
        "sections": outline.sections,
        "version": outline.version,
        "completeness": completeness(outline.sections or {}, SAGA_OUTLINE_SECTIONS),
    }


@router.patch("/{saga_id}/outline")
async def update_outline(
    saga_id: uuid.UUID, payload: OutlineUpdate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    outline = await get_or_create_outline(db, saga_id)
    outline.sections = merge_sections(
        outline.sections or blank_sections(SAGA_OUTLINE_SECTIONS), payload.sections, SAGA_OUTLINE_SECTIONS
    )
    outline.version = (outline.version or 0) + 1
    await db.commit()
    await db.refresh(outline)
    return {
        "saga_id": str(saga_id),
        "sections": outline.sections,
        "version": outline.version,
        "completeness": completeness(outline.sections or {}, SAGA_OUTLINE_SECTIONS),
    }


# --------------------------------------------------------------------------
# Series / phase plans
# --------------------------------------------------------------------------


@router.get("/{saga_id}/series")
async def list_series(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SeriesPlan).where(SeriesPlan.saga_id == saga_id).order_by(SeriesPlan.position.asc())
    )
    plans = result.scalars().all()
    return {
        "series": [
            {
                "id": str(plan.id),
                "name": plan.name,
                "kind": plan.kind,
                "position": plan.position,
                "version": plan.version,
                "sections": plan.sections,
                "section_status": plan.section_status,
                "completeness": completeness(plan.sections or {}, SERIES_PLAN_SECTIONS),
            }
            for plan in plans
        ]
    }


@router.post("/{saga_id}/series", status_code=status.HTTP_201_CREATED)
async def create_series(
    saga_id: uuid.UUID, payload: SeriesPlanCreate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    position = payload.position
    if position is None:
        result = await db.execute(
            select(func.coalesce(func.max(SeriesPlan.position), 0)).where(SeriesPlan.saga_id == saga_id)
        )
        position = int(result.scalar_one() or 0) + 1
    sections = merge_sections(blank_sections(SERIES_PLAN_SECTIONS), payload.sections, SERIES_PLAN_SECTIONS)
    if not sections["identity"].get("name"):
        sections["identity"]["name"] = payload.name
    plan = SeriesPlan(
        saga_id=saga_id,
        name=payload.name,
        kind=payload.kind,
        position=position,
        sections=sections,
        section_status={},
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "kind": plan.kind,
        "position": plan.position,
        "sections": plan.sections,
        "completeness": completeness(plan.sections or {}, SERIES_PLAN_SECTIONS),
    }


@router.patch("/{saga_id}/series/{plan_id}")
async def update_series(
    saga_id: uuid.UUID, plan_id: uuid.UUID, payload: SeriesPlanUpdate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SeriesPlan).where(SeriesPlan.id == plan_id, SeriesPlan.saga_id == saga_id)
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series plan not found")
    if payload.name:
        plan.name = payload.name
    if payload.kind:
        plan.kind = payload.kind
    if payload.position is not None:
        plan.position = payload.position
    if payload.sections is not None:
        plan.sections = merge_sections(
            plan.sections or blank_sections(SERIES_PLAN_SECTIONS), payload.sections, SERIES_PLAN_SECTIONS
        )
        plan.version = (plan.version or 0) + 1
    if payload.section_status is not None:
        merged_status = dict(plan.section_status or {})
        merged_status.update(payload.section_status)
        plan.section_status = merged_status
    await db.commit()
    await db.refresh(plan)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "kind": plan.kind,
        "position": plan.position,
        "version": plan.version,
        "sections": plan.sections,
        "completeness": completeness(plan.sections or {}, SERIES_PLAN_SECTIONS),
    }


@router.delete("/{saga_id}/series/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_series(saga_id: uuid.UUID, plan_id: uuid.UUID, db: Db, user: CurrentUser) -> None:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SeriesPlan).where(SeriesPlan.id == plan_id, SeriesPlan.saga_id == saga_id)
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series plan not found")
    await db.delete(plan)
    await db.commit()


# --------------------------------------------------------------------------
# Promise / thread ledger
# --------------------------------------------------------------------------


@router.get("/{saga_id}/threads")
async def list_threads(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaThread)
        .where(SagaThread.saga_id == saga_id)
        .order_by(SagaThread.sort_order.asc(), SagaThread.created_at.asc())
    )
    threads = result.scalars().all()
    return {
        "threads": [
            {
                "id": str(t.id),
                "name": t.name,
                "detail": t.detail,
                "status": t.status,
                "opened_in": t.opened_in,
                "paid_in": t.paid_in,
                "notes": t.notes,
                "sort_order": t.sort_order,
            }
            for t in threads
        ],
        "counts": await thread_counts(db, saga_id),
    }


@router.post("/{saga_id}/threads", status_code=status.HTTP_201_CREATED)
async def create_thread(
    saga_id: uuid.UUID, payload: ThreadCreate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    thread = SagaThread(saga_id=saga_id, **payload.model_dump())
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return {"id": str(thread.id), "name": thread.name, "status": thread.status}


@router.patch("/{saga_id}/threads/{thread_id}")
async def update_thread(
    saga_id: uuid.UUID, thread_id: uuid.UUID, payload: ThreadUpdate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaThread).where(SagaThread.id == thread_id, SagaThread.saga_id == saga_id)
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(thread, key, value)
    await db.commit()
    await db.refresh(thread)
    return {
        "id": str(thread.id),
        "name": thread.name,
        "detail": thread.detail,
        "status": thread.status,
        "opened_in": thread.opened_in,
        "paid_in": thread.paid_in,
        "notes": thread.notes,
        "sort_order": thread.sort_order,
    }


@router.delete("/{saga_id}/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(saga_id: uuid.UUID, thread_id: uuid.UUID, db: Db, user: CurrentUser) -> None:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaThread).where(SagaThread.id == thread_id, SagaThread.saga_id == saga_id)
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    await db.delete(thread)
    await db.commit()


# --------------------------------------------------------------------------
# Truth / knowledge ledger
# --------------------------------------------------------------------------


@router.get("/{saga_id}/truths")
async def list_truths(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaTruth)
        .where(SagaTruth.saga_id == saga_id)
        .order_by(SagaTruth.sort_order.asc(), SagaTruth.created_at.asc())
    )
    truths = result.scalars().all()
    return {
        "truths": [
            {
                "id": str(t.id),
                "statement": t.statement,
                "level": t.level,
                "status": t.status,
                "knows": t.knows or [],
                "believes_otherwise": t.believes_otherwise or [],
                "reveal_point": t.reveal_point,
                "notes": t.notes,
                "sort_order": t.sort_order,
            }
            for t in truths
        ],
        "counts": await truth_counts(db, saga_id),
    }


@router.post("/{saga_id}/truths", status_code=status.HTTP_201_CREATED)
async def create_truth(saga_id: uuid.UUID, payload: TruthCreate, db: Db, user: CurrentUser) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    truth = SagaTruth(saga_id=saga_id, **payload.model_dump())
    db.add(truth)
    await db.commit()
    await db.refresh(truth)
    return {"id": str(truth.id), "statement": truth.statement, "status": truth.status}


@router.patch("/{saga_id}/truths/{truth_id}")
async def update_truth(
    saga_id: uuid.UUID, truth_id: uuid.UUID, payload: TruthUpdate, db: Db, user: CurrentUser
) -> dict[str, Any]:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaTruth).where(SagaTruth.id == truth_id, SagaTruth.saga_id == saga_id)
    )
    truth = result.scalar_one_or_none()
    if truth is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truth not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(truth, key, value)
    await db.commit()
    await db.refresh(truth)
    return {
        "id": str(truth.id),
        "statement": truth.statement,
        "level": truth.level,
        "status": truth.status,
        "knows": truth.knows or [],
        "believes_otherwise": truth.believes_otherwise or [],
        "reveal_point": truth.reveal_point,
        "notes": truth.notes,
        "sort_order": truth.sort_order,
    }


@router.delete("/{saga_id}/truths/{truth_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_truth(saga_id: uuid.UUID, truth_id: uuid.UUID, db: Db, user: CurrentUser) -> None:
    await get_saga_or_404(db, saga_id, user.id)
    result = await db.execute(
        select(SagaTruth).where(SagaTruth.id == truth_id, SagaTruth.saga_id == saga_id)
    )
    truth = result.scalar_one_or_none()
    if truth is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truth not found")
    await db.delete(truth)
    await db.commit()


# --------------------------------------------------------------------------
# Project membership + overview
# --------------------------------------------------------------------------


@router.post("/{saga_id}/projects", status_code=status.HTTP_201_CREATED)
async def link_project(
    saga_id: uuid.UUID, payload: LinkProject, db: Db, user: CurrentUser
) -> dict[str, Any]:
    saga = await get_saga_or_404(db, saga_id, user.id)
    project = await get_project_or_404(db, payload.project_id, user.id)
    project.saga_id = saga.id
    if getattr(project, "scope", "series") == "standalone":
        project.scope = "series"
    await db.commit()
    return {"saga_id": str(saga.id), "project_id": str(project.id), "scope": project.scope}


@router.delete("/{saga_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_project(saga_id: uuid.UUID, project_id: uuid.UUID, db: Db, user: CurrentUser) -> None:
    await get_saga_or_404(db, saga_id, user.id)
    project = await get_project_or_404(db, project_id, user.id)
    if project.saga_id == saga_id:
        project.saga_id = None
        await db.commit()


@router.get("/{saga_id}/overview")
async def saga_overview(saga_id: uuid.UUID, db: Db, user: CurrentUser) -> dict[str, Any]:
    saga = await get_saga_or_404(db, saga_id, user.id)
    outline = await get_or_create_outline(db, saga_id)
    threads = await thread_counts(db, saga_id)
    truths = await truth_counts(db, saga_id)
    projects = await linked_projects(db, saga_id)
    owed = sum(count for status_key, count in threads.items() if status_key in ("open", "developing"))
    unrevealed = sum(count for status_key, count in truths.items() if status_key in ("hidden", "clued"))
    return {
        "saga_id": str(saga_id),
        "name": saga.name,
        "bible": completeness(saga.sections or {}, SAGA_SECTIONS),
        "outline": completeness(outline.sections or {}, SAGA_OUTLINE_SECTIONS),
        "projects": projects,
        "threads": threads,
        "promises_owed": owed,
        "truths": truths,
        "truths_unrevealed": unrevealed,
        "books": sum(p["book_count"] for p in projects),
    }
