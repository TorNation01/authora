"""AI model role overrides - load/save from DB for admin UI."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models.setting import Setting
from authora.services.model_role_registry import ROLE_IDS, get_ollama_model_for_role

AI_MODEL_ROLES_KEY = "ai_model_roles"


async def get_effective_model_overrides(
    db: AsyncSession,
    db_overrides: dict[str, str],
    available_models: set[str] | None = None,
) -> dict[str, str]:
    """
    Apply hardware-tier fallback when assigned models are missing.
    If available_models provided and Ollama enabled, pick first available from preferred/fallback.
    """
    from authora.config import get_settings
    from authora.services.hardware_tier import get_hardware_tier
    from authora.services.hardware_model_mapping import apply_fallback_to_mappings

    settings = get_settings()
    if not settings.ollama_enabled or not available_models:
        return db_overrides

    current = {role: get_ollama_model_for_role(role, db_overrides=db_overrides) for role in ROLE_IDS}
    profile = get_hardware_tier(getattr(settings, "ollama_hardware_tier", None))
    return apply_fallback_to_mappings(current, available_models, profile.tier)


async def get_ai_model_role_overrides(db: AsyncSession) -> dict[str, str]:
    """Load role->model overrides from Setting. Returns {} if none."""
    result = await db.execute(select(Setting).where(Setting.key == AI_MODEL_ROLES_KEY))
    row = result.scalar_one_or_none()
    if not row or not isinstance(row.value, dict):
        return {}
    return {k: str(v) for k, v in row.value.items() if k in ROLE_IDS and v}


async def save_ai_model_role_overrides(
    db: AsyncSession,
    overrides: dict[str, str],
) -> dict[str, str]:
    """Save role->model overrides to Setting. Only valid roles are stored."""
    filtered = {k: str(v).strip() for k, v in overrides.items() if k in ROLE_IDS and str(v).strip()}
    result = await db.execute(select(Setting).where(Setting.key == AI_MODEL_ROLES_KEY))
    row = result.scalar_one_or_none()
    if not row:
        row = Setting(key=AI_MODEL_ROLES_KEY, value=filtered)
        db.add(row)
    else:
        row.value = filtered
    await db.flush()
    return filtered
