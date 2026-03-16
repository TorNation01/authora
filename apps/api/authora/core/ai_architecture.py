"""
AI Architecture Foundation - AUTHORA.

Modular, provider-agnostic AI engine supporting:
- Multiple providers (OpenAI, Anthropic, Ollama, future)
- Task-based routing
- Per-project and per-user preferences
- Local and cloud hybrid
- Fallback and retry
- Safety and observability
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Provider category."""

    CLOUD = "cloud"
    LOCAL = "local"


class RoutingMode(str, Enum):
    """User-selectable routing preference."""

    AUTO = "auto"  # Best available, local-first when possible
    QUALITY_FIRST = "quality_first"  # Premium models preferred
    SPEED_FIRST = "speed_first"  # Fast models preferred
    PRIVACY_FIRST = "privacy_first"  # Local-only when available
    LOCAL_FIRST = "local_first"  # Prefer Ollama, fallback to cloud
    CLOUD_ONLY = "cloud_only"  # OpenAI/Anthropic only


class TaskCategory(str, Enum):
    """Task category for routing and capability matching."""

    WRITING_ASSIST = "writing_assist"
    FICTION_IDEATION = "fiction_ideation"
    NONFICTION_STRUCTURE = "nonfiction_structure"
    GHOSTWRITING = "ghostwriting"
    EDITING_POLISH = "editing_polish"
    SUMMARIZATION = "summarization"
    BRAINSTORMING = "brainstorming"
    EXTRACTION = "extraction"
    GENERAL = "general"


@dataclass
class ProviderCapability:
    """Provider capability metadata."""

    name: str
    provider_type: ProviderType
    supports_streaming: bool = True
    max_context_tokens: int = 128000
    supports_tools: bool = False
    supports_vision: bool = False
    typical_latency_ms: int | None = None
    cost_per_1k_input: float | None = None
    cost_per_1k_output: float | None = None
    is_available: bool = True


@dataclass
class TaskMetadata:
    """Task metadata for routing and prompt selection."""

    task_id: str
    category: TaskCategory
    ideal_model_characteristics: list[str] = field(default_factory=list)
    context_needs: list[str] = field(default_factory=list)
    safety_rules: list[str] = field(default_factory=list)
    requires_factual_grounding: bool = False
    local_acceptable: bool = True
    premium_preferred: bool = False
    max_context_chars: int = 8000
    output_format: str | None = None


@dataclass
class RoutingContext:
    """Context for model routing decisions."""

    task_id: str
    task_category: TaskCategory
    content_sensitivity: str = "normal"
    content_length_chars: int = 0
    context_size_chars: int = 0
    user_plan: str | None = None
    project_settings: dict[str, Any] | None = None
    user_preferences: dict[str, Any] | None = None
    routing_mode: RoutingMode = RoutingMode.AUTO
    preferred_provider: str | None = None
    preferred_model: str | None = None
    privacy_mode: bool = False
    offline_mode: bool = False
