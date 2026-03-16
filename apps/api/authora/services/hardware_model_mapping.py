"""Hardware-tier-based default model mappings for Ollama."""

from typing import Any

from authora.services.hardware_tier import HardwareTierId, get_hardware_tier
from authora.services.model_role_registry import (
    ROLE_DEFAULT_WRITING,
    ROLE_EDITING_POLISH,
    ROLE_EMBEDDINGS,
    ROLE_FICTION_IDEATION,
    ROLE_NONFICTION_STRUCTURE,
    ROLE_OPTIONAL_VISION,
    ROLE_PREMIUM_DRAFTING,
    ROLE_QUICK_ASSIST,
    ROLE_SUMMARIZATION,
    ROLE_IDS,
)

# Per-tier recommended models. Each role maps to a list of models in preference order.
# First available in Ollama is used when resolving.
# "disabled" for optional_vision means do not use vision model.

TIER_MODEL_MAPPINGS: dict[HardwareTierId, dict[str, list[str]]] = {
    "1": {
        ROLE_QUICK_ASSIST: ["qwen3:4b"],
        ROLE_DEFAULT_WRITING: ["qwen3:4b"],
        ROLE_PREMIUM_DRAFTING: ["qwen3:8b"],
        ROLE_FICTION_IDEATION: ["qwen3:8b"],
        ROLE_NONFICTION_STRUCTURE: ["qwen3:8b"],
        ROLE_EDITING_POLISH: ["qwen3:4b"],
        ROLE_SUMMARIZATION: ["qwen3:4b"],
        ROLE_EMBEDDINGS: ["qwen3-embedding:0.6b", "qwen3-embedding:4b"],
        ROLE_OPTIONAL_VISION: ["disabled"],
    },
    "2": {
        ROLE_QUICK_ASSIST: ["qwen3:4b"],
        ROLE_DEFAULT_WRITING: ["qwen3:8b"],
        ROLE_PREMIUM_DRAFTING: ["qwen3:14b"],
        ROLE_FICTION_IDEATION: ["qwen3:8b", "qwen3:14b"],
        ROLE_NONFICTION_STRUCTURE: ["qwen3:8b", "qwen3:14b"],
        ROLE_EDITING_POLISH: ["qwen3:8b"],
        ROLE_SUMMARIZATION: ["qwen3:4b"],
        ROLE_EMBEDDINGS: ["qwen3-embedding:4b", "mxbai-embed-large"],
        ROLE_OPTIONAL_VISION: ["disabled"],
    },
    "3": {
        ROLE_QUICK_ASSIST: ["qwen3:4b"],
        ROLE_DEFAULT_WRITING: ["qwen3:8b"],
        ROLE_PREMIUM_DRAFTING: ["qwen3:14b", "qwen3:30b"],
        ROLE_FICTION_IDEATION: ["qwen3:14b", "qwen3:30b"],
        ROLE_NONFICTION_STRUCTURE: ["qwen3:14b", "qwen3:30b"],
        ROLE_EDITING_POLISH: ["qwen3:8b", "qwen3:14b"],
        ROLE_SUMMARIZATION: ["qwen3:4b", "qwen3:8b"],
        ROLE_EMBEDDINGS: ["qwen3-embedding:4b", "qwen3-embedding:8b", "mxbai-embed-large"],
        ROLE_OPTIONAL_VISION: ["qwen3-vl:8b"],
    },
    "4": {
        ROLE_QUICK_ASSIST: ["qwen3:4b"],
        ROLE_DEFAULT_WRITING: ["qwen3:8b", "qwen3:14b"],
        ROLE_PREMIUM_DRAFTING: ["qwen3:30b", "qwen3:32b"],
        ROLE_FICTION_IDEATION: ["qwen3:14b", "qwen3:30b", "qwen3:32b"],
        ROLE_NONFICTION_STRUCTURE: ["qwen3:14b", "qwen3:30b", "qwen3:32b"],
        ROLE_EDITING_POLISH: ["qwen3:14b"],
        ROLE_SUMMARIZATION: ["qwen3:4b", "qwen3:8b"],
        ROLE_EMBEDDINGS: ["qwen3-embedding:8b", "mxbai-embed-large"],
        ROLE_OPTIONAL_VISION: ["qwen3-vl:8b"],
    },
}

# RAG/context limits per tier (chunks, size, overlap)
TIER_RAG_LIMITS: dict[HardwareTierId, dict[str, int]] = {
    "1": {"rag_max_chunks": 3, "rag_chunk_size": 600, "rag_chunk_overlap": 80},
    "2": {"rag_max_chunks": 5, "rag_chunk_size": 800, "rag_chunk_overlap": 100},
    "3": {"rag_max_chunks": 7, "rag_chunk_size": 1000, "rag_chunk_overlap": 120},
    "4": {"rag_max_chunks": 10, "rag_chunk_size": 1200, "rag_chunk_overlap": 150},
}


def get_tier_recommended_mapping(tier: HardwareTierId) -> dict[str, str]:
    """Return single-model-per-role mapping for tier (first choice only)."""
    mapping = TIER_MODEL_MAPPINGS.get(tier, TIER_MODEL_MAPPINGS["1"])
    return {role: (candidates[0] if candidates else "disabled") for role, candidates in mapping.items()}


def resolve_model_with_fallback(
    role: str,
    preferred_models: list[str],
    available_models: set[str],
    fallback_chain: list[str] | None = None,
) -> str | None:
    """
    Pick first available model from preferred list, or from fallback_chain.
    Returns None for optional_vision when 'disabled'.
    """
    if preferred_models and preferred_models[0] == "disabled":
        return None

    for m in preferred_models:
        if m in available_models:
            return m
    # Try fallback chain (smaller models)
    if fallback_chain:
        for m in fallback_chain:
            if m in available_models:
                return m
    return preferred_models[0] if preferred_models else None  # Use first even if not available; caller validates


def get_fallback_chain_for_role(role: str) -> list[str]:
    """Ordered list of smaller fallback models for a role (cross-tier)."""
    # Universal fallbacks: smaller models that work for most roles
    if role == ROLE_EMBEDDINGS:
        return ["qwen3-embedding:4b", "qwen3-embedding:0.6b", "nomic-embed-text"]
    if role == ROLE_OPTIONAL_VISION:
        return []  # No fallback for vision
    return ["qwen3:8b", "qwen3:4b", "llama3.2"]


def apply_fallback_to_mappings(
    mappings: dict[str, str],
    available_models: set[str],
    tier: str,
) -> dict[str, str]:
    """
    Apply fallback when assigned models are missing. Returns effective mappings.
    For each role, if assigned model not in available_models, pick first available
    from tier preferred list or fallback chain.
    """
    from authora.services.hardware_tier import TIER_IDS

    tier_id = tier if tier in TIER_IDS else "1"
    tier_preferred = TIER_MODEL_MAPPINGS.get(tier_id, TIER_MODEL_MAPPINGS["1"])
    result: dict[str, str] = {}

    for role in ROLE_IDS:
        assigned = mappings.get(role)
        if assigned and assigned in available_models:
            result[role] = assigned
            continue
        preferred = tier_preferred.get(role, [])
        if preferred and preferred[0] == "disabled" and role == ROLE_OPTIONAL_VISION:
            result[role] = "qwen3:4b"  # Use lightweight text model when vision disabled
            continue
        resolved = resolve_model_with_fallback(
            role,
            preferred,
            available_models,
            get_fallback_chain_for_role(role),
        )
        result[role] = resolved or assigned or "llama3.2"
    return result


async def get_available_ollama_models(base_url: str) -> set[str]:
    """Fetch set of model names from Ollama."""
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    try:
        p = OllamaProvider(base_url=base_url, model="")
        raw = await p.list_models()
        return {m.get("name") for m in raw if m.get("name")}
    except Exception:
        return set()


def get_rag_limits_for_tier(tier: HardwareTierId) -> dict[str, int]:
    """Return RAG limits for tier."""
    return dict(TIER_RAG_LIMITS.get(tier, TIER_RAG_LIMITS["1"]))
