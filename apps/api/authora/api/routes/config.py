"""Config API - deployment mode, feature flags, branding for frontend."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.database import get_db
from authora.models import Setting

router = APIRouter(prefix="/config", tags=["config"])

# Cache config responses for 60s to reduce DB load on repeated frontend loads
_CONFIG_CACHE: dict[str, tuple[dict, float]] = {}
_CONFIG_CACHE_TTL = 60.0


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


def _get_cached(key: str) -> dict | None:
    now = time.time()
    if key in _CONFIG_CACHE:
        data, expiry = _CONFIG_CACHE[key]
        if now < expiry:
            return data
        del _CONFIG_CACHE[key]
    return None


def _set_cached(key: str, data: dict) -> None:
    _CONFIG_CACHE[key] = (data, time.time() + _CONFIG_CACHE_TTL)


@router.get("/mode")
async def get_mode(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return deployment mode and feature flags. Public endpoint for frontend bootstrap. Cached 60s."""
    cached = _get_cached("mode")
    if cached is not None:
        return cached
    settings = get_settings()
    data = {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": await _merged_feature_flags(db),
        "integration_flags": settings.get_integration_flags(),
    }
    _set_cached("mode", data)
    return data


@router.get("/branding")
async def get_branding():
    """Return white-label branding config. Public endpoint."""
    settings = get_settings()
    return settings.get_branding()


@router.get("")
async def get_config(db: Annotated[AsyncSession, Depends(get_db)]):
    """Combined config for frontend. Public endpoint. Cached 60s."""
    cached = _get_cached("full")
    if cached is not None:
        return cached
    settings = get_settings()
    data = {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": await _merged_feature_flags(db),
        "integration_flags": settings.get_integration_flags(),
        "branding": settings.get_branding(),
    }
    _set_cached("full", data)
    return data


@router.get("/ai")
async def get_ai_config():
    """AI provider config for frontend. Public endpoint. Cached 60s."""
    cached = _get_cached("ai")
    if cached is not None:
        return cached
    from authora.services.ai_registry import list_available_providers
    from authora.services.embedding_service import is_embeddings_configured

    settings = get_settings()
    providers = list_available_providers()
    data = {
        "provider_mode": settings.ai_provider_mode,
        "providers": providers,
        "ollama_enabled": settings.ollama_enabled,
        "ollama_base_url": settings.ollama_base_url if settings.ollama_enabled else None,
        "has_ai": bool(settings.openai_api_key or settings.anthropic_api_key or settings.ollama_enabled),
        "embeddings_enabled": is_embeddings_configured(),
        "rag_max_chunks": settings.rag_max_chunks,
    }
    _set_cached("ai", data)
    return data
