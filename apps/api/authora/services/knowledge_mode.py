"""Knowledge mode service: default modules per mode, enabled modules for project."""

from authora.models.project import KNOWLEDGE_MODES

# Module IDs used across modes. Same backend entities may map to different module IDs per mode.
KNOWLEDGE_MODULE_DEFAULTS: dict[str, list[str]] = {
    "fiction": [
        "characters",
        "locations",
        "timeline",
        "relationships",
        "themes",
        "ideas",
        "research",
        "sources",
    ],
    "nonfiction": [
        "concepts",
        "framework",
        "chapter_promise",
        "sources",
        "claims",
        "methodology",
        "research",
        "ideas",
    ],
    "memoir": [
        "people",
        "timeline",
        "memories",
        "reflections",
        "themes",
        "sources",
        "research",
        "ideas",
        "private_notes",
    ],
    "workbook": [
        "prompts",
        "exercises",
        "transformation",
        "modules",
        "outcome",
        "research",
        "ideas",
    ],
    "hybrid": [
        "characters",
        "people",
        "locations",
        "concepts",
        "framework",
        "chapter_promise",
        "timeline",
        "relationships",
        "themes",
        "ideas",
        "research",
        "sources",
        "claims",
        "methodology",
        "memories",
        "reflections",
        "private_notes",
        "prompts",
        "exercises",
        "transformation",
        "modules",
        "outcome",
    ],
}

# Human-readable labels for UI
KNOWLEDGE_MODULE_LABELS: dict[str, str] = {
    "characters": "Character Bible",
    "people": "People Map",
    "locations": "Worldbuilding / Locations",
    "concepts": "Concept Map",
    "framework": "Framework Map",
    "chapter_promise": "Chapter Promise Tracker",
    "timeline": "Timeline / Events",
    "relationships": "Relationship Mapping",
    "themes": "Themes / Motifs",
    "ideas": "Idea Capture",
    "research": "Research Vault",
    "sources": "Source Manager",
    "claims": "Claims / References",
    "methodology": "Methodology Notes",
    "memories": "Memory Capture",
    "reflections": "Reflection Notes",
    "private_notes": "Private / Sensitivity Notes",
    "prompts": "Prompt Bank",
    "exercises": "Exercise Blocks",
    "transformation": "Transformation Path",
    "modules": "Module Structure",
    "outcome": "Reader Outcome Tracking",
}


def get_enabled_modules(knowledge_mode: str, knowledge_modules: list[str] | None) -> list[str]:
    """Return enabled module IDs for a project. Uses override if set, else mode defaults."""
    if knowledge_modules is not None and len(knowledge_modules) > 0:
        return knowledge_modules
    return KNOWLEDGE_MODULE_DEFAULTS.get(knowledge_mode, KNOWLEDGE_MODULE_DEFAULTS["fiction"])


def is_module_enabled(
    knowledge_mode: str,
    knowledge_modules: list[str] | None,
    module_id: str,
) -> bool:
    """Check if a module is enabled for the project."""
    enabled = get_enabled_modules(knowledge_mode, knowledge_modules)
    return module_id in enabled


def get_module_label(module_id: str) -> str:
    """Human-readable label for a module."""
    return KNOWLEDGE_MODULE_LABELS.get(module_id, module_id)
