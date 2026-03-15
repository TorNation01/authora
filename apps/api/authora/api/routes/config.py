"""Config API - deployment mode, feature flags, branding for frontend."""

from fastapi import APIRouter

from authora.config import get_settings

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/mode")
async def get_mode():
    """Return deployment mode and feature flags. Public endpoint for frontend bootstrap."""
    settings = get_settings()
    return {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": settings.get_feature_flags(),
        "integration_flags": settings.get_integration_flags(),
    }


@router.get("/branding")
async def get_branding():
    """Return white-label branding config. Public endpoint."""
    settings = get_settings()
    return settings.get_branding()


@router.get("")
async def get_config():
    """Combined config for frontend. Public endpoint."""
    settings = get_settings()
    return {
        "deployment_mode": settings.deployment_mode,
        "app_mode": settings.effective_app_mode(),
        "is_standalone": settings.is_standalone(),
        "is_anakatech": settings.is_anakatech(),
        "is_white_label": settings.is_white_label(),
        "feature_flags": settings.get_feature_flags(),
        "integration_flags": settings.get_integration_flags(),
        "branding": settings.get_branding(),
    }
