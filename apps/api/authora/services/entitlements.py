"""Entitlements service - unified feature/limit checks for commercialization.

Thin abstraction over billing_service. Use this for consistent gating across
the app. When feature_billing is False, all checks pass (premium-equivalent).
Optional Anakatech shared entitlement check when integration enabled.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.services.billing_service import (
    check_ai_action_limit,
    check_book_limit,
    check_export_limit,
    check_ghostwriter_limit,
    check_project_limit,
    check_storage_limit,
    get_user_plan,
    has_feature,
)


async def _check_shared_entitlement_if_enabled(user_id: UUID, feature: str) -> tuple[bool, str | None] | None:
    """If shared billing enabled, check Anakatech entitlement. Returns (allowed, error) or None to skip."""
    try:
        from authora.integration.billing import check_shared_entitlement, use_shared_entitlements
        if not use_shared_entitlements():
            return None
        allowed, err = await check_shared_entitlement(user_id, feature)
        return (allowed, err)
    except Exception:
        return None


async def check_can_create_project(db: AsyncSession, user_id: UUID) -> tuple[bool, str | None]:
    """Check if user can create a project. Returns (allowed, error_message)."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "projects")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "Project creation not allowed."
    if not get_settings().feature_billing:
        return True, None
    allowed, current, limit = await check_project_limit(db, user_id)
    if not allowed:
        return False, f"Project limit reached ({current}/{limit}). Upgrade for more."
    return True, None


async def check_can_create_book(db: AsyncSession, user_id: UUID) -> tuple[bool, str | None]:
    """Check if user can create a book."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "books")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "Book creation not allowed."
    if not get_settings().feature_billing:
        return True, None
    allowed, current, limit = await check_book_limit(db, user_id)
    if not allowed:
        return False, f"Book limit reached ({current}/{limit}). Upgrade for more."
    return True, None


async def check_can_use_ai(db: AsyncSession, user_id: UUID) -> tuple[bool, str | None]:
    """Check if user can run an AI action."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "ai")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "AI assistance not allowed."
    if not get_settings().feature_billing:
        return True, None
    if not await has_feature(db, user_id, "ai"):
        return False, "AI assistance requires a paid plan."
    allowed, used, limit = await check_ai_action_limit(db, user_id)
    if not allowed:
        return False, f"AI action limit reached ({used}/{limit} this month)."
    return True, None


async def check_can_export(db: AsyncSession, user_id: UUID, format: str) -> tuple[bool, str | None]:
    """Check if user can export in given format."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "export")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "Export not allowed."
    if not get_settings().feature_billing:
        return True, None
    allowed, used, limit = await check_export_limit(db, user_id, format)
    if not allowed:
        if used >= limit:
            return False, f"Export limit reached ({used}/{limit} this month)."
        return False, f"Export to {format.upper()} requires a paid plan."
    return True, None


async def check_can_use_ghostwriter(db: AsyncSession, user_id: UUID) -> tuple[bool, str | None]:
    """Check if user can use ghostwriter mode."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "ghostwriter")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "Ghostwriter not allowed."
    if not get_settings().feature_billing:
        return True, None
    if not await has_feature(db, user_id, "ghostwriter"):
        return False, "Ghostwriter mode requires a paid plan."
    allowed, used, limit = await check_ghostwriter_limit(db, user_id)
    if not allowed:
        return False, f"Ghostwriter limit reached ({used}/{limit} this month)."
    return True, None


async def check_can_use_storage(db: AsyncSession, user_id: UUID, additional_mb: int = 0) -> tuple[bool, str | None]:
    """Check if user has storage headroom."""
    shared = await _check_shared_entitlement_if_enabled(user_id, "storage")
    if shared is not None:
        allowed, err = shared
        if not allowed:
            return False, err or "Storage not allowed."
    if not get_settings().feature_billing:
        return True, None
    allowed, used_mb, limit_mb = await check_storage_limit(db, user_id, additional_mb)
    if not allowed:
        return False, f"Storage limit reached ({used_mb}/{limit_mb} MB)."
    return True, None


async def get_effective_plan(db: AsyncSession, user_id: UUID):
    """Get user's effective plan (for display)."""
    return await get_user_plan(db, user_id)
