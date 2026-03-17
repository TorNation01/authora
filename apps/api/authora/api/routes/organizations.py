"""Organization API - enterprise multi-tenant management."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.models import Organization
from authora.services.org_service import (
    add_member,
    create_organization,
    get_member,
    get_org_by_id,
    get_user_orgs,
    require_org_role,
    update_org_branding,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


class OrgCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=100)
    domain: str | None = Field(None, max_length=255)
    branding: dict[str, Any] | None = None
    onboarding_config: dict[str, Any] | None = None


class OrgBrandingUpdate(BaseModel):
    product_name: str | None = None
    tagline: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    primary_color: str | None = None
    show_powered_by: bool | None = None


class OrgMemberAdd(BaseModel):
    user_id: uuid.UUID
    role: str = Field("user", pattern="^(admin|manager|user)$")


class OrgResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    domain: str | None
    branding: dict[str, Any]
    onboarding_config: dict[str, Any]
    is_active: bool

    class Config:
        from_attributes = True


class OrgMemberResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    role: str


def _require_tenant_aware() -> None:
    if not get_settings().feature_tenant_aware:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizations are not enabled in this deployment",
        )


@router.get("", response_model=list[OrgResponse])
async def list_organizations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """List organizations the current user belongs to."""
    _require_tenant_aware()
    orgs = await get_user_orgs(db, current_user.id)
    return [OrgResponse.model_validate(o) for o in orgs]


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    data: OrgCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Create organization. Caller becomes admin."""
    _require_tenant_aware()
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required to create orgs")
    try:
        org = await create_organization(
            db,
            data.name,
            slug=data.slug,
            domain=data.domain,
            branding=data.branding,
            onboarding_config=data.onboarding_config,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await add_member(db, org.id, current_user.id, role="admin")
    await db.commit()
    await db.refresh(org)
    return OrgResponse.model_validate(org)


@router.get("/{org_id}", response_model=OrgResponse)
async def get_organization(
    org_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get organization. Requires membership."""
    _require_tenant_aware()
    org = await get_org_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    member = await require_org_role(db, org_id, current_user.id, "user")
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
    return OrgResponse.model_validate(org)


@router.patch("/{org_id}/branding", response_model=OrgResponse)
async def update_org_branding_route(
    org_id: uuid.UUID,
    data: OrgBrandingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Update org branding. Requires admin or manager."""
    _require_tenant_aware()
    org = await get_org_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    member = await require_org_role(db, org_id, current_user.id, "manager")
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or admin required")
    branding = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if branding:
        await update_org_branding(db, org_id, branding)
    await db.commit()
    await db.refresh(org)
    return OrgResponse.model_validate(org)


@router.post("/{org_id}/members", status_code=status.HTTP_201_CREATED)
async def add_org_member(
    org_id: uuid.UUID,
    data: OrgMemberAdd,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Add member to org. Requires admin or manager."""
    _require_tenant_aware()
    org = await get_org_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    member = await require_org_role(db, org_id, current_user.id, "manager")
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or admin required")
    existing = await get_member(db, org_id, data.user_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already a member")
    try:
        m = await add_member(db, org_id, data.user_id, role=data.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(m.id), "org_id": str(org_id), "user_id": str(data.user_id), "role": m.role}

