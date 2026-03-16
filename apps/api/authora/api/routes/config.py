"""Config API - deployment mode, feature flags, branding for frontend."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.database import get_db
from authora.models import Setting

router = APIRouter(prefix="/config", tags=["config"])


async def _merged_feature_flags(db: AsyncSession) -> dict[str, bool]:
    """Merge env feature flags with DB overrides (Setting feature.*). Env is base; DB overrides."""
    env_flags = get_settings().get_feature_flags()
    try:
        result = await db.execute(select(Setting).where(Setting.key.like("feature.%")))
        rows = result.scalars().all()
        merged = dict(env_flags)
        for row in rows:
            if isinstance(row.value, dict) and "enabled" in row.value:
                key = row.key.replace("feature.", "", 1)
                if key in merged:
                    merged[key] = bool(row.value["enabled"])
        return merged
    except Exception:
        return env_flags  # Fallback to env-only when DB unavailable


@router.get("/mode")
async def get_mode(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return deployment mode and feature flags. Public endpoint for frontend bootstrap."""
    settings = get_settings()
    return {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": await _merged_feature_flags(db),
        "integration_flags": settings.get_integration_flags(),
    }


@router.get("/branding")
async def get_branding():
    """Return white-label branding config. Public endpoint."""
    settings = get_settings()
    return settings.get_branding()


@router.get("")
async def get_config(db: Annotated[AsyncSession, Depends(get_db)]):
    """Combined config for frontend. Public endpoint."""
    settings = get_settings()
    return {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": await _merged_feature_flags(db),
        "integration_flags": settings.get_integration_flags(),
        "branding": settings.get_branding(),
    }
