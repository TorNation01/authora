"""Organization service - CRUD, membership, tenant resolution."""

import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import OrgMember, OrgSubscription, Organization, User

ORG_ROLES = ("admin", "manager", "user")
DEFAULT_TENANT_SLUG = "default"


def _slugify(name: str) -> str:
    """Generate URL-safe slug from name."""
    s = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[-\s]+", "-", s).strip("-")[:100]


async def get_org_by_id(db: AsyncSession, org_id: uuid.UUID) -> Organization | None:
    """Get organization by ID."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    return result.scalar_one_or_none()


async def get_org_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    """Get organization by slug."""
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    return result.scalar_one_or_none()


async def get_org_by_domain(db: AsyncSession, domain: str) -> Organization | None:
    """Get organization by custom domain."""
    result = await db.execute(select(Organization).where(Organization.domain == domain))
    return result.scalar_one_or_none()


async def resolve_tenant(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    domain: str | None = None,
) -> Organization | None:
    """Resolve tenant from tenant_id or domain. Returns None for standalone."""
    if tenant_id:
        return await get_org_by_id(db, tenant_id)
    if domain:
        return await get_org_by_domain(db, domain)
    return None


async def create_organization(
    db: AsyncSession,
    name: str,
    *,
    slug: str | None = None,
    domain: str | None = None,
    branding: dict[str, Any] | None = None,
    onboarding_config: dict[str, Any] | None = None,
) -> Organization:
    """Create organization. Slug derived from name if not provided."""
    s = slug or _slugify(name)
    existing = await get_org_by_slug(db, s)
    if existing:
        raise ValueError(f"Organization slug '{s}' already exists")
    org = Organization(
        name=name,
        slug=s,
        domain=domain,
        branding=branding or {},
        onboarding_config=onboarding_config or {},
    )
    db.add(org)
    await db.flush()
    return org


async def update_org_branding(
    db: AsyncSession,
    org_id: uuid.UUID,
    branding: dict[str, Any],
) -> Organization | None:
    """Update organization branding. Merges with existing."""
    org = await get_org_by_id(db, org_id)
    if not org:
        return None
    merged = {**org.branding, **branding}
    org.branding = merged
    await db.flush()
    return org


async def add_member(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = "user",
) -> OrgMember:
    """Add user to organization with role."""
    if role not in ORG_ROLES:
        raise ValueError(f"Invalid role. Must be one of {ORG_ROLES}")
    member = OrgMember(org_id=org_id, user_id=user_id, role=role)
    db.add(member)
    await db.flush()
    return member


async def get_member(db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID) -> OrgMember | None:
    """Get org membership."""
    result = await db.execute(
        select(OrgMember).where(OrgMember.org_id == org_id, OrgMember.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_orgs(db: AsyncSession, user_id: uuid.UUID) -> list[Organization]:
    """Get organizations user belongs to."""
    result = await db.execute(
        select(Organization)
        .join(OrgMember, OrgMember.org_id == Organization.id)
        .where(OrgMember.user_id == user_id, Organization.is_active == True)
    )
    return list(result.scalars().all())


async def require_org_role(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    min_role: str,
) -> OrgMember | None:
    """Require user has at least min_role in org. admin > manager > user."""
    member = await get_member(db, org_id, user_id)
    if not member:
        return None
    order = {"admin": 3, "manager": 2, "user": 1}
    if order.get(member.role, 0) < order.get(min_role, 0):
        return None
    return member


async def get_org_subscription(db: AsyncSession, org_id: uuid.UUID) -> OrgSubscription | None:
    """Get active org subscription."""
    result = await db.execute(
        select(OrgSubscription)
        .where(OrgSubscription.org_id == org_id, OrgSubscription.status == "active")
        .order_by(OrgSubscription.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
