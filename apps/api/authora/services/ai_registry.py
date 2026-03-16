"""AI provider registry - multi-provider support, task routing, fallback chain."""

from dataclasses import dataclass
from typing import Any

from authora.config import get_settings
from authora.services.model_role_registry import (
    get_cloud_model_for_role,
    get_ollama_model_for_role,
    task_to_role,
)

# Task types for model routing
TASK_WRITING_ASSIST = "writing_assist"
TASK_FICTION_IDEATION = "fiction_ideation"
TASK_NONFICTION_STRUCTURE = "nonfiction_structure"
TASK_GHOSTWRITING = "ghostwriting"
TASK_EDITING_POLISH = "editing_polish"
TASK_SUMMARIZATION = "summarization"
TASK_GENERAL = "general"

TASK_TYPES = [
    TASK_WRITING_ASSIST,
    TASK_FICTION_IDEATION,
    TASK_NONFICTION_STRUCTURE,
    TASK_GHOSTWRITING,
    TASK_EDITING_POLISH,
    TASK_SUMMARIZATION,
    TASK_GENERAL,
]

# Map action_id to task type
ACTION_TO_TASK: dict[str, str] = {
    "rewrite_sentence": TASK_EDITING_POLISH,
    "rewrite_paragraph": TASK_EDITING_POLISH,
    "improve_wording": TASK_EDITING_POLISH,
    "improve_flow": TASK_EDITING_POLISH,
    "expand": TASK_WRITING_ASSIST,
    "condense": TASK_EDITING_POLISH,
    "change_tone": TASK_WRITING_ASSIST,
    "continue_draft": TASK_WRITING_ASSIST,
    "generate_outline": TASK_FICTION_IDEATION,
    "generate_scene_ideas": TASK_FICTION_IDEATION,
    "generate_chapter_ideas": TASK_FICTION_IDEATION,
    "generate_examples": TASK_WRITING_ASSIST,
    "summarize_chapter": TASK_SUMMARIZATION,
    "suggest_chapter_names": TASK_WRITING_ASSIST,
    "fix_transitions": TASK_EDITING_POLISH,
    "create_hook": TASK_WRITING_ASSIST,
    "create_conclusion": TASK_WRITING_ASSIST,
    "help_when_stuck": TASK_WRITING_ASSIST,
    "notes_to_prose": TASK_WRITING_ASSIST,
    "generate_section": TASK_GHOSTWRITING,
    "summarize_section": TASK_SUMMARIZATION,
    "title_brainstorm": TASK_FICTION_IDEATION,
    "blurb_copy": TASK_GHOSTWRITING,
    "research_note_summary": TASK_EDITING_POLISH,
    "vault_retrieval_summary": TASK_EDITING_POLISH,
    "identify_repetition": TASK_EDITING_POLISH,
    "suggest_transitions": TASK_EDITING_POLISH,
    "style_guidance": TASK_EDITING_POLISH,
    "freeform_creative": TASK_GENERAL,
}


def action_to_task(action_id: str, book_type: str = "general") -> str:
    """Map action_id to task. Nonfiction outline/structure uses nonfiction_structure."""
    task = ACTION_TO_TASK.get(action_id, TASK_GENERAL)
    if task == TASK_FICTION_IDEATION and book_type == "nonfiction":
        return TASK_NONFICTION_STRUCTURE
    return task


@dataclass
class ProviderConfig:
    """Provider config for registry."""

    name: str
    enabled: bool
    is_local: bool
    priority: int  # lower = higher priority in fallback


def _get_provider_instances() -> dict[str, Any]:
    """Build provider instances from config. Lazy to avoid circular imports."""
    from authora.services.ai_provider import (
        AnthropicProvider,
        OpenAIProvider,
    )
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    settings = get_settings()
    providers: dict[str, Any] = {}
    cloud_disabled = getattr(settings, "ai_cloud_disabled", False)
    local_only = getattr(settings, "ai_local_only", False)

    if not local_only and not cloud_disabled and settings.openai_api_key:
        providers["openai"] = OpenAIProvider()
    if not local_only and not cloud_disabled and settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider()
    if settings.ollama_enabled:
        providers["ollama"] = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model_default,
        )
    return providers


def get_providers_for_mode(mode: str) -> list[str]:
    """Return provider list for mode: auto, local_first, cloud, local, quality_first, speed_first, privacy_first."""
    settings = get_settings()
    instances = _get_provider_instances()
    if not instances:
        return []

    local = [p for p in ["ollama"] if p in instances]
    cloud = [p for p in ["openai", "anthropic"] if p in instances]

    if mode in ("local", "privacy_first", "strict_privacy"):
        return local
    if mode == "cloud" or mode == "cloud_only":
        return cloud
    if mode == "local_first" or mode == "auto":
        return local + cloud if local else cloud
    if mode == "quality_first":
        return cloud + local if cloud else local
    if mode == "speed_first":
        return local + cloud if local else cloud
    return local + cloud if local else cloud


def get_provider_for_task(
    task: str = TASK_GENERAL,
    project_prefs: dict[str, Any] | None = None,
    user_prefs: dict[str, Any] | None = None,
    preferred_provider: str | None = None,
    preferred_model: str | None = None,
    mode: str | None = None,
    db_overrides: dict[str, str] | None = None,
) -> tuple[Any, str, str]:
    """
    Get (provider, model, provider_name) for a task.
    Uses project prefs, preferred provider/model, then config routing.
    Returns (None, "", "") if no provider available.
    """
    settings = get_settings()
    effective_mode = (
        mode
        or (project_prefs.get("routing_mode") or project_prefs.get("ai_mode")) if project_prefs else None
    )
    effective_mode = effective_mode or getattr(settings, "ai_provider_mode", "auto")

    providers_ordered = get_providers_for_mode(effective_mode or "auto")
    instances = _get_provider_instances()

    if preferred_provider and preferred_provider in instances and preferred_provider in providers_ordered:
        p = instances[preferred_provider]
        model = preferred_model or _get_model_for_task(
            p, task, preferred_provider, db_overrides, project_prefs, user_prefs
        )
        return p, model, preferred_provider

    for provider_name in providers_ordered:
        if provider_name not in instances:
            continue
        provider = instances[provider_name]
        model = _get_model_for_task(
            provider, task, provider_name, db_overrides, project_prefs, user_prefs
        )
        return provider, model, provider_name

    return None, "", ""


def _get_model_for_task(
    provider: Any,
    task: str,
    provider_name: str,
    db_overrides: dict[str, str] | None = None,
    project_prefs: dict[str, Any] | None = None,
    user_prefs: dict[str, Any] | None = None,
) -> str:
    """Resolve model for task and provider via role-based registry."""
    settings = get_settings()
    if provider_name == "ollama":
        role = task_to_role(task)
        return get_ollama_model_for_role(
            role,
            project_prefs=project_prefs,
            user_prefs=user_prefs,
            db_overrides=db_overrides,
        )
    if provider_name == "openai":
        role = task_to_role(task)
        return get_cloud_model_for_role(role, "openai", settings.ai_model)
    if provider_name == "anthropic":
        role = task_to_role(task)
        return get_cloud_model_for_role(role, "anthropic", settings.ai_model)
    return settings.ai_model or "gpt-4o-mini"


def get_fallback_chain(
    task: str,
    provider_name: str,
    mode: str | None = None,
    db_overrides: dict[str, str] | None = None,
    project_prefs: dict[str, Any] | None = None,
    user_prefs: dict[str, Any] | None = None,
) -> list[tuple[Any, str, str]]:
    """
    Get fallback chain: [(provider, model, name), ...] after primary.
    When mode is local, privacy_first, or strict_privacy: no cloud fallback.
    """
    settings = get_settings()
    effective_mode = (
        mode
        or (project_prefs.get("routing_mode") or project_prefs.get("ai_mode") if project_prefs else None)
        or settings.ai_provider_mode
    )
    providers_ordered = get_providers_for_mode(effective_mode or "auto")
    instances = _get_provider_instances()

    # Strict privacy / local-only: no fallback to cloud
    if effective_mode in ("local", "privacy_first", "strict_privacy"):
        if provider_name == "ollama":
            return []
        return []

    chain: list[tuple[Any, str, str]] = []
    started = False
    for name in providers_ordered:
        if name == provider_name:
            started = True
            continue
        if not started or name not in instances:
            continue
        p = instances[name]
        model = _get_model_for_task(p, task, name, db_overrides, project_prefs, user_prefs)
        chain.append((p, model, name))
    return chain


def list_available_providers() -> list[dict]:
    """List providers with enabled status."""
    settings = get_settings()
    instances = _get_provider_instances()
    result = []
    for name, p in instances.items():
        is_local = name == "ollama"
        result.append({
            "name": name,
            "enabled": True,
            "is_local": is_local,
            "model_default": getattr(settings, "ai_model", "gpt-4o-mini") if name != "ollama" else settings.ollama_model_default,
        })
    return result
