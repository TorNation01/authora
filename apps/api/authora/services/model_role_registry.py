"""Model-role mapping registry for Ollama and cloud AI."""

from typing import Any

from authora.config import get_settings

# Legacy single-tier defaults (used when hardware tier not applicable)
# Role identifiers
ROLE_QUICK_ASSIST = "quick_assist_model"
ROLE_DEFAULT_WRITING = "default_writing_model"
ROLE_PREMIUM_DRAFTING = "premium_drafting_model"
ROLE_FICTION_IDEATION = "fiction_ideation_model"
ROLE_NONFICTION_STRUCTURE = "nonfiction_structure_model"
ROLE_EDITING_POLISH = "editing_polish_model"
ROLE_SUMMARIZATION = "summarization_model"
ROLE_EMBEDDINGS = "embeddings_model"
ROLE_OPTIONAL_VISION = "optional_vision_model"

ROLE_IDS = [
    ROLE_QUICK_ASSIST,
    ROLE_DEFAULT_WRITING,
    ROLE_PREMIUM_DRAFTING,
    ROLE_FICTION_IDEATION,
    ROLE_NONFICTION_STRUCTURE,
    ROLE_EDITING_POLISH,
    ROLE_SUMMARIZATION,
    ROLE_EMBEDDINGS,
    ROLE_OPTIONAL_VISION,
]

# Recommended default Ollama models
OLLAMA_DEFAULT_MODELS: dict[str, str] = {
    ROLE_QUICK_ASSIST: "qwen3:4b",
    ROLE_DEFAULT_WRITING: "qwen3:8b",
    ROLE_PREMIUM_DRAFTING: "qwen3:14b",
    ROLE_FICTION_IDEATION: "qwen3:8b",
    ROLE_NONFICTION_STRUCTURE: "qwen3:8b",
    ROLE_EDITING_POLISH: "qwen3:8b",
    ROLE_SUMMARIZATION: "qwen3:4b",
    ROLE_EMBEDDINGS: "qwen3-embedding:4b",
    ROLE_OPTIONAL_VISION: "qwen3-vl:8b",
}

# Cloud fallback models (when local unavailable)
CLOUD_FALLBACK_MODELS: dict[str, dict[str, str]] = {
    ROLE_QUICK_ASSIST: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_DEFAULT_WRITING: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_PREMIUM_DRAFTING: {"openai": "gpt-4o", "anthropic": "claude-3-5-sonnet-20241022"},
    ROLE_FICTION_IDEATION: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_NONFICTION_STRUCTURE: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_EDITING_POLISH: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_SUMMARIZATION: {"openai": "gpt-4o-mini", "anthropic": "claude-3-haiku-20240307"},
    ROLE_EMBEDDINGS: {"openai": "text-embedding-3-small", "anthropic": ""},
    ROLE_OPTIONAL_VISION: {"openai": "gpt-4o", "anthropic": "claude-3-5-sonnet-20241022"},
}

# Task types from ai_registry
TASK_WRITING_ASSIST = "writing_assist"
TASK_FICTION_IDEATION = "fiction_ideation"
TASK_NONFICTION_STRUCTURE = "nonfiction_structure"
TASK_GHOSTWRITING = "ghostwriting"
TASK_EDITING_POLISH = "editing_polish"
TASK_SUMMARIZATION = "summarization"
TASK_GENERAL = "general"

# Map task to role (for model resolution)
TASK_TO_ROLE: dict[str, str] = {
    TASK_WRITING_ASSIST: ROLE_QUICK_ASSIST,
    TASK_FICTION_IDEATION: ROLE_FICTION_IDEATION,
    TASK_NONFICTION_STRUCTURE: ROLE_NONFICTION_STRUCTURE,
    TASK_GHOSTWRITING: ROLE_PREMIUM_DRAFTING,
    TASK_EDITING_POLISH: ROLE_EDITING_POLISH,
    TASK_SUMMARIZATION: ROLE_SUMMARIZATION,
    TASK_GENERAL: ROLE_DEFAULT_WRITING,
}

# Config attr names for each role (getattr(settings, key))
ROLE_CONFIG_KEYS: dict[str, str] = {
    ROLE_QUICK_ASSIST: "ollama_model_quick_assist",
    ROLE_DEFAULT_WRITING: "ollama_model_default_writing",
    ROLE_PREMIUM_DRAFTING: "ollama_model_premium_drafting",
    ROLE_FICTION_IDEATION: "ollama_model_fiction_ideation",
    ROLE_NONFICTION_STRUCTURE: "ollama_model_nonfiction_structure",
    ROLE_EDITING_POLISH: "ollama_model_editing_polish",
    ROLE_SUMMARIZATION: "ollama_model_summarization",
    ROLE_EMBEDDINGS: "ollama_model_embeddings",
    ROLE_OPTIONAL_VISION: "ollama_model_optional_vision",
}


def task_to_role(task: str) -> str:
    """Map task to role. Ghostwriting uses premium_drafting."""
    return TASK_TO_ROLE.get(task, ROLE_DEFAULT_WRITING)


def _get_tier_default_for_role(role: str) -> str:
    """Get tier-based default model for role. Uses hardware tier from config."""
    from authora.services.hardware_tier import get_hardware_tier
    from authora.services.hardware_model_mapping import get_tier_recommended_mapping

    settings = get_settings()
    configured = getattr(settings, "ollama_hardware_tier", None)
    profile = get_hardware_tier(configured)
    mapping = get_tier_recommended_mapping(profile.tier)
    model = mapping.get(role)
    if model and model != "disabled":
        return model
    if model == "disabled" and role == ROLE_OPTIONAL_VISION:
        return settings.ollama_model_default  # Use default text model when vision disabled
    return OLLAMA_DEFAULT_MODELS.get(role, settings.ollama_model_default)


def get_ollama_model_for_role(
    role: str,
    project_prefs: dict[str, Any] | None = None,
    user_prefs: dict[str, Any] | None = None,
    db_overrides: dict[str, str] | None = None,
) -> str:
    """
    Resolve Ollama model for a role.
    Order: project preferred_ollama_model > project model_roles[role] > user preferred_ollama_model >
           db_overrides > env > tier defaults > OLLAMA_DEFAULT_MODELS.
    """
    # Per-project preferred local model (overrides all roles)
    if project_prefs and project_prefs.get("preferred_ollama_model"):
        return project_prefs["preferred_ollama_model"]
    # Per-project per-role override
    if project_prefs and role in project_prefs.get("model_roles", {}):
        return project_prefs["model_roles"][role]
    # Per-user preferred local model (when permitted by plan/admin)
    if user_prefs and user_prefs.get("preferred_ollama_model"):
        return user_prefs["preferred_ollama_model"]

    if db_overrides and role in db_overrides:
        return db_overrides[role]

    settings = get_settings()
    env_key = ROLE_CONFIG_KEYS.get(role)
    if env_key:
        val = getattr(settings, env_key, None)
        if val:
            return val

    return _get_tier_default_for_role(role) or OLLAMA_DEFAULT_MODELS.get(role, settings.ollama_model_default)


def get_cloud_model_for_role(role: str, provider: str, settings_ai_model: str | None) -> str:
    """Resolve cloud model for a role when falling back from local."""
    fallbacks = CLOUD_FALLBACK_MODELS.get(role, {})
    model = fallbacks.get(provider) or settings_ai_model or "gpt-4o-mini"
    return model if model else "gpt-4o-mini"


def get_all_role_mappings(
    db_overrides: dict[str, str] | None = None,
) -> dict[str, dict[str, str]]:
    """Return current role -> {ollama, openai, anthropic} mappings for admin UI."""
    settings = get_settings()
    result: dict[str, dict[str, str]] = {}
    for role in ROLE_IDS:
        ollama = get_ollama_model_for_role(role, db_overrides=db_overrides)
        result[role] = {
            "ollama": ollama,
            "openai": CLOUD_FALLBACK_MODELS.get(role, {}).get("openai", settings.ai_model or "gpt-4o-mini"),
            "anthropic": CLOUD_FALLBACK_MODELS.get(role, {}).get("anthropic", settings.ai_model or "claude-3-haiku-20240307"),
        }
    return result
