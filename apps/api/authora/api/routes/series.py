"""Series bible API - the canon that sits above the individual books.

One document per project. Same mechanics as the book bible: the schema drives
the questionnaire, the client sends partial sections, the server merges and
reports completeness so the process step can derive its real state.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_project_or_404
from authora.data.series_bible_schema import SECTIONS, blank_sections, completeness, merge_sections
from authora.database import get_db
from authora.models import SeriesBible

router = APIRouter(prefix="/projects", tags=["series"])

Db = Annotated[AsyncSession, Depends(get_db)]


class SeriesUpdate(BaseModel):
    sections: dict[str, Any] = Field(default_factory=dict)
    section_status: dict[str, str] | None = None


class SeriesResponse(BaseModel):
    project_id: uuid.UUID
    sections: dict[str, Any]
    section_status: dict[str, str]
    version: int
    updated_at: datetime | None = None
    completeness: dict[str, Any]


async def get_or_create_series(db: AsyncSession, project_id: uuid.UUID) -> SeriesBible:
    result = await db.execute(select(SeriesBible).where(SeriesBible.project_id == project_id))
    bible = result.scalar_one_or_none()
    if bible is None:
        bible = SeriesBible(project_id=project_id, sections=blank_sections(), section_status={})
        db.add(bible)
        await db.commit()
        await db.refresh(bible)
    else:
        merged = merge_sections(blank_sections(), bible.sections or {})
        if merged != (bible.sections or {}):
            bible.sections = merged
            await db.commit()
            await db.refresh(bible)
    return bible


def _payload(bible: SeriesBible) -> SeriesResponse:
    sections = bible.sections or {}
    return SeriesResponse(
        project_id=bible.project_id,
        sections=sections,
        section_status=bible.section_status or {},
        version=bible.version,
        updated_at=bible.updated_at,
        completeness=completeness(sections),
    )


@router.get("/series/schema")
async def series_schema(_: CurrentUser):
    """The series-canon questionnaire the web app renders."""
    return {"sections": SECTIONS}


@router.get("/{project_id}/series", response_model=SeriesResponse)
async def get_series(project_id: uuid.UUID, current_user: CurrentUser, db: Db):
    await get_project_or_404(db, project_id, current_user.id)
    bible = await get_or_create_series(db, project_id)
    return _payload(bible)


@router.patch("/{project_id}/series", response_model=SeriesResponse)
async def update_series(
    project_id: uuid.UUID,
    payload: SeriesUpdate,
    current_user: CurrentUser,
    db: Db,
):
    await get_project_or_404(db, project_id, current_user.id)
    bible = await get_or_create_series(db, project_id)

    merged = merge_sections(bible.sections or {}, payload.sections or {})
    status_map = dict(bible.section_status or {})
    if payload.section_status:
        valid = {s["key"] for s in SECTIONS}
        for key, value in payload.section_status.items():
            if key in valid and value in ("working", "locked", "undecided"):
                status_map[key] = value

    bible.sections = merged
    bible.section_status = status_map
    bible.version = (bible.version or 1) + 1
    await db.commit()
    await db.refresh(bible)
    return _payload(bible)
