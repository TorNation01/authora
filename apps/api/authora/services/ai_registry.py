"""AI provider registry - multi-provider support, task routing, fallback chain."""

from dataclasses import dataclass
from typing import Any

from authora.config import get_settings

# Task types for model routing
TASK_WRITING_ASSIST = "writing_assist"
TASK_FICTION_IDEATION = "fiction_ideation"
TASK_NONFICTION_STRUCTURE = "nonfiction_structure"
TASK_GHOSTWRITING = "ghostwriting"
TASK_EDITING_POLISH = "editing_polish"
TASK_GENERAL = "general"

TASK_TYPES = [
    TASK_WRITING_ASSIST,
    TASK_FICTION_IDEATION,
    TASK_NONFICTION_STRUCTURE,
    TASK_GHOSTWRITING,
    TASK_EDITING_POLISH,
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
    "summarize_chapter": TASK_EDITING_POLISH,
    "suggest_chapter_names": TASK_WRITING_ASSIST,
    "fix_transitions": TASK_EDITING_POLISH,
    "create_hook": TASK_WRITING_ASSIST,
    "create_conclusion": TASK_WRITING_ASSIST,
    "help_when_stuck": TASK_WRITING_ASSIST,
    "notes_to_prose": TASK_WRITING_ASSIST,
    "generate_section": TASK_GHOSTWRITING,
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

    if settings.openai_api_key:
        providers["openai"] = OpenAIProvider()
    if settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider()
    if settings.ollama_enabled:
        providers["ollama"] = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model_default,
        )
    return providers


def get_providers_for_mode(mode: str) -> list[str]:
    """Return provider list for mode: auto (local first), cloud, local."""
    settings = get_settings()
    instances = _get_provider_instances()
    if not instances:
        return []

    local = [p for p in ["ollama"] if p in instances]
    cloud = [p for p in ["openai", "anthropic"] if p in instances]

    if mode == "local":
        return local
    if mode == "cloud":
        return cloud
    # auto: prefer local, fallback to cloud
    return local + cloud if local else cloud


def get_provider_for_task(
    task: str = TASK_GENERAL,
    project_prefs: dict[str, Any] | None = None,
    preferred_provider: str | None = None,
    preferred_model: str | None = None,
    mode: str | None = None,
) -> tuple[Any, str, str]:
    """
    Get (provider, model, provider_name) for a task.
    Uses project prefs, preferred provider/model, then config routing.
    Returns (None, "", "") if no provider available.
    """
    settings = get_settings()
    effective_mode = mode or project_prefs.get("ai_mode") if project_prefs else None
    effective_mode = effective_mode or settings.ai_provider_mode

    providers_ordered = get_providers_for_mode(effective_mode)
    instances = _get_provider_instances()

    if preferred_provider and preferred_provider in instances and preferred_provider in providers_ordered:
        p = instances[preferred_provider]
        model = preferred_model or _get_model_for_task(p, task, preferred_provider)
        return p, model, preferred_provider

    for provider_name in providers_ordered:
        if provider_name not in instances:
            continue
        provider = instances[provider_name]
        model = _get_model_for_task(provider, task, provider_name)
        return provider, model, provider_name

    return None, "", ""


def _get_model_for_task(provider: Any, task: str, provider_name: str) -> str:
    """Resolve model for task and provider."""
    settings = get_settings()
    if provider_name == "ollama":
        return settings.get_ollama_model_for_task(task)
    if provider_name == "openai":
        return settings.ai_model or "gpt-4o-mini"
    if provider_name == "anthropic":
        return settings.ai_model or "claude-3-haiku-20240307"
    return settings.ai_model or "gpt-4o-mini"


def get_fallback_chain(task: str, provider_name: str, mode: str | None = None) -> list[tuple[Any, str, str]]:
    """Get fallback chain: [(provider, model, name), ...] after primary."""
    settings = get_settings()
    effective_mode = mode or settings.ai_provider_mode
    providers_ordered = get_providers_for_mode(effective_mode)
    instances = _get_provider_instances()

    chain: list[tuple[Any, str, str]] = []
    started = False
    for name in providers_ordered:
        if name == provider_name:
            started = True
            continue
        if not started or name not in instances:
            continue
        p = instances[name]
        model = _get_model_for_task(p, task, name)
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
