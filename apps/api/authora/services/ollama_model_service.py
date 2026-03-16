"""
Ollama multi-model service - model discovery, capability tagging, per-model test.

Supports:
- Detect installed Ollama models
- Capability tagging per model (stored in Setting)
- Per-model test prompt
- Model timeout settings
- Offline/unavailable state handling
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Setting

OLLAMA_MODEL_CAPABILITIES_KEY = "ollama_model_capabilities"
OLLAMA_MODEL_TIMEOUT_KEY = "ollama_model_timeout"
DEFAULT_TEST_PROMPT = "Write one short sentence about writing."
DEFAULT_REQUEST_TIMEOUT = 120


async def get_ollama_models_with_metadata(
    db: AsyncSession,
    base_url: str | None = None,
) -> list[dict[str, Any]]:
    """
    List installed Ollama models with capability tags and metadata.
    Returns list of {name, size, capabilities, recommended_roles}.
    """
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    settings = get_settings()
    url = base_url or settings.ollama_base_url
    capabilities = await get_model_capabilities(db)

    try:
        p = OllamaProvider(base_url=url, model="")
        raw = await p.list_models()
    except Exception:
        return []

    result = []
    for m in raw:
        name = m.get("name")
        if not name:
            continue
        meta = capabilities.get(name, {})
        result.append({
            "name": name,
            "size": m.get("size"),
            "capabilities": meta.get("capabilities", []),
            "recommended_roles": meta.get("recommended_roles", []),
            "enabled": meta.get("enabled", True),
        })
    return result


async def get_model_capabilities(db: AsyncSession) -> dict[str, dict[str, Any]]:
    """Get per-model capability tags from Setting."""
    result = await db.execute(select(Setting).where(Setting.key == OLLAMA_MODEL_CAPABILITIES_KEY))
    row = result.scalar_one_or_none()
    return (row.value or {}) if row and row.value else {}


async def set_model_capabilities(
    db: AsyncSession,
    model_name: str,
    capabilities: list[str] | None = None,
    recommended_roles: list[str] | None = None,
    enabled: bool | None = None,
) -> dict[str, Any]:
    """Update capability tags for a model."""
    result = await db.execute(select(Setting).where(Setting.key == OLLAMA_MODEL_CAPABILITIES_KEY))
    row = result.scalar_one_or_none()
    data = dict((row.value or {})) if row and row.value else {}

    if model_name not in data:
        data[model_name] = {}
    meta = dict(data[model_name])
    if capabilities is not None:
        meta["capabilities"] = capabilities
    if recommended_roles is not None:
        meta["recommended_roles"] = recommended_roles
    if enabled is not None:
        meta["enabled"] = enabled
    data[model_name] = meta

    if not row:
        row = Setting(key=OLLAMA_MODEL_CAPABILITIES_KEY, value=data)
        db.add(row)
    else:
        row.value = data
    await db.flush()
    return meta


async def get_request_timeout(db: AsyncSession) -> int:
    """Get Ollama request timeout in seconds (from Setting or config)."""
    result = await db.execute(select(Setting).where(Setting.key == OLLAMA_MODEL_TIMEOUT_KEY))
    row = result.scalar_one_or_none()
    if row and row.value and isinstance(row.value, dict):
        return int(row.value.get("seconds", DEFAULT_REQUEST_TIMEOUT))
    return getattr(get_settings(), "ollama_request_timeout", None) or DEFAULT_REQUEST_TIMEOUT


async def set_request_timeout(db: AsyncSession, seconds: int) -> None:
    """Set Ollama request timeout."""
    result = await db.execute(select(Setting).where(Setting.key == OLLAMA_MODEL_TIMEOUT_KEY))
    row = result.scalar_one_or_none()
    value = {"seconds": max(30, min(300, seconds))}
    if not row:
        row = Setting(key=OLLAMA_MODEL_TIMEOUT_KEY, value=value)
        db.add(row)
    else:
        row.value = value
    await db.flush()


async def test_model(
    model_name: str,
    base_url: str | None = None,
    test_prompt: str | None = None,
    timeout: float | None = None,
) -> tuple[bool, str]:
    """
    Run a test prompt against a model. Returns (ok, message).
    """
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    settings = get_settings()
    url = base_url or settings.ollama_base_url
    prompt = test_prompt or DEFAULT_TEST_PROMPT
    to = timeout or getattr(settings, "ollama_request_timeout", DEFAULT_REQUEST_TIMEOUT)

    try:
        p = OllamaProvider(base_url=url, model=model_name)
        async for _ in p.complete_stream(prompt, "You are a helpful assistant.", max_tokens=50):
            break
        return True, "Model responded successfully"
    except Exception as e:
        return False, str(e)


async def check_ollama_health(base_url: str | None = None) -> tuple[bool, str]:
    """Check Ollama host health. Returns (ok, message)."""
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    settings = get_settings()
    url = base_url or settings.ollama_base_url
    try:
        p = OllamaProvider(base_url=url, model="")
        return await p.health_check()
    except Exception as e:
        return False, str(e)
