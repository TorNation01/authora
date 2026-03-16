"""
AI Task Catalog - formal task definitions for AUTHORA.

Each task defines: ideal model characteristics, context needs, safety rules,
output formatting, whether factual grounding is required, whether local model
is acceptable, whether premium model is preferred.
"""

from dataclasses import dataclass, field

from authora.core.ai_architecture import TaskCategory


@dataclass
class AITaskDefinition:
    """Formal AI task definition."""

    id: str
    label: str
    description: str
    category: TaskCategory
    ideal_model_characteristics: list[str] = field(default_factory=list)
    context_needs: list[str] = field(default_factory=list)
    safety_rules: list[str] = field(default_factory=list)
    requires_factual_grounding: bool = False
    local_acceptable: bool = True
    premium_preferred: bool = False
    max_context_chars: int = 8000
    max_tokens: int = 1024
    uses_selection: bool = True
    uses_context: bool = True
    output_format: str | None = None


# Full task catalog with metadata
AI_TASK_CATALOG: dict[str, AITaskDefinition] = {
    # Brainstorming
    "generate_scene_ideas": AITaskDefinition(
        id="generate_scene_ideas",
        label="Generate scene ideas",
        description="Generate scene ideas for fiction.",
        category=TaskCategory.FICTION_IDEATION,
        ideal_model_characteristics=["creative", "varied output"],
        context_needs=["premise", "genre", "recent context"],
        safety_rules=["no plagiarism", "original ideas"],
        local_acceptable=True,
        premium_preferred=False,
        uses_selection=False,
        uses_context=True,
        max_tokens=1024,
    ),
    "generate_chapter_ideas": AITaskDefinition(
        id="generate_chapter_ideas",
        label="Generate chapter ideas",
        description="Generate chapter-level ideas and directions.",
        category=TaskCategory.FICTION_IDEATION,
        ideal_model_characteristics=["creative", "structural thinking"],
        context_needs=["outline", "premise", "genre"],
        local_acceptable=True,
        uses_selection=False,
        uses_context=True,
        max_tokens=1024,
    ),
    "generate_outline": AITaskDefinition(
        id="generate_outline",
        label="Generate outline",
        description="Generate outline from context.",
        category=TaskCategory.NONFICTION_STRUCTURE,
        ideal_model_characteristics=["structural", "logical"],
        context_needs=["topic", "premise", "genre"],
        local_acceptable=True,
        uses_selection=False,
        uses_context=True,
        max_tokens=1024,
    ),
    # Rewriting
    "rewrite_sentence": AITaskDefinition(
        id="rewrite_sentence",
        label="Rewrite sentence",
        description="Rewrite for clarity or style.",
        category=TaskCategory.EDITING_POLISH,
        ideal_model_characteristics=["preserves voice", "minimal change"],
        safety_rules=["preserve author voice", "suggestions only"],
        local_acceptable=True,
        uses_selection=True,
        max_tokens=256,
    ),
    "rewrite_paragraph": AITaskDefinition(
        id="rewrite_paragraph",
        label="Rewrite paragraph",
        description="Rewrite the selected paragraph.",
        category=TaskCategory.EDITING_POLISH,
        ideal_model_characteristics=["preserves voice", "improves flow"],
        safety_rules=["preserve author voice"],
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "improve_wording": AITaskDefinition(
        id="improve_wording",
        label="Improve wording",
        description="Suggest better word choices.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "improve_flow": AITaskDefinition(
        id="improve_flow",
        label="Improve flow",
        description="Improve transitions and readability.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "expand": AITaskDefinition(
        id="expand",
        label="Expand",
        description="Expand with more detail.",
        category=TaskCategory.WRITING_ASSIST,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=1024,
    ),
    "condense": AITaskDefinition(
        id="condense",
        label="Condense",
        description="Make more concise.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "change_tone": AITaskDefinition(
        id="change_tone",
        label="Change tone",
        description="Change tone (formal, casual, etc.).",
        category=TaskCategory.WRITING_ASSIST,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Continuation
    "continue_draft": AITaskDefinition(
        id="continue_draft",
        label="Continue draft",
        description="Continue from where the text ends.",
        category=TaskCategory.WRITING_ASSIST,
        ideal_model_characteristics=["style mimicry", "coherent continuation"],
        safety_rules=["preserve voice", "suggestions only"],
        premium_preferred=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=2048,
    ),
    # Summarization
    "summarize_chapter": AITaskDefinition(
        id="summarize_chapter",
        label="Summarize chapter",
        description="Summarize the chapter.",
        category=TaskCategory.SUMMARIZATION,
        requires_factual_grounding=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "summarize_section": AITaskDefinition(
        id="summarize_section",
        label="Summarize section",
        description="Summarize manuscript section.",
        category=TaskCategory.SUMMARIZATION,
        requires_factual_grounding=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Structure
    "suggest_chapter_names": AITaskDefinition(
        id="suggest_chapter_names",
        label="Suggest chapter names",
        description="Suggest chapter title options.",
        category=TaskCategory.BRAINSTORMING,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=256,
    ),
    "fix_transitions": AITaskDefinition(
        id="fix_transitions",
        label="Fix transitions",
        description="Improve transitions between sections.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "create_hook": AITaskDefinition(
        id="create_hook",
        label="Create hook/opening",
        description="Create an engaging opening.",
        category=TaskCategory.WRITING_ASSIST,
        local_acceptable=True,
        uses_selection=False,
        uses_context=True,
        max_tokens=512,
    ),
    "create_conclusion": AITaskDefinition(
        id="create_conclusion",
        label="Create conclusion",
        description="Create a strong conclusion.",
        category=TaskCategory.WRITING_ASSIST,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Ghostwriting
    "generate_section": AITaskDefinition(
        id="generate_section",
        label="Generate section",
        description="Generate section from brief.",
        category=TaskCategory.GHOSTWRITING,
        ideal_model_characteristics=["long-form", "coherent narrative"],
        premium_preferred=True,
        local_acceptable=True,
        safety_rules=["clearly AI-generated", "user reviews before use"],
        uses_selection=False,
        uses_context=True,
        max_tokens=2048,
    ),
    "notes_to_prose": AITaskDefinition(
        id="notes_to_prose",
        label="Notes to prose",
        description="Convert notes to prose.",
        category=TaskCategory.GHOSTWRITING,
        requires_factual_grounding=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=1024,
    ),
    # Help
    "help_when_stuck": AITaskDefinition(
        id="help_when_stuck",
        label="Help when stuck",
        description="Suggest what to write next.",
        category=TaskCategory.BRAINSTORMING,
        local_acceptable=True,
        uses_selection=True,
        uses_context=True,
        max_tokens=1024,
    ),
    "generate_examples": AITaskDefinition(
        id="generate_examples",
        label="Generate examples",
        description="Generate illustrative examples.",
        category=TaskCategory.WRITING_ASSIST,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Marketing / copy
    "title_brainstorm": AITaskDefinition(
        id="title_brainstorm",
        label="Title brainstorm",
        description="Brainstorm book/section titles.",
        category=TaskCategory.BRAINSTORMING,
        local_acceptable=True,
        uses_selection=False,
        uses_context=True,
        max_tokens=256,
    ),
    "blurb_copy": AITaskDefinition(
        id="blurb_copy",
        label="Blurb copy",
        description="Write blurb/marketing copy.",
        category=TaskCategory.GHOSTWRITING,
        local_acceptable=True,
        premium_preferred=True,
        uses_selection=False,
        uses_context=True,
        max_tokens=512,
    ),
    # Research / vault
    "research_note_summary": AITaskDefinition(
        id="research_note_summary",
        label="Research note summary",
        description="Summarize research notes.",
        category=TaskCategory.SUMMARIZATION,
        requires_factual_grounding=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "vault_retrieval_summary": AITaskDefinition(
        id="vault_retrieval_summary",
        label="Vault retrieval summary",
        description="Summarize vault-retrieved content.",
        category=TaskCategory.EXTRACTION,
        requires_factual_grounding=True,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Consistency / style
    "identify_repetition": AITaskDefinition(
        id="identify_repetition",
        label="Identify repetition",
        description="Identify repetitive phrasing.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    "suggest_transitions": AITaskDefinition(
        id="suggest_transitions",
        label="Suggest transitions",
        description="Suggest transition phrases.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=256,
    ),
    "style_guidance": AITaskDefinition(
        id="style_guidance",
        label="Style guidance",
        description="Provide style consistency guidance.",
        category=TaskCategory.EDITING_POLISH,
        local_acceptable=True,
        uses_selection=True,
        max_tokens=512,
    ),
    # Freeform
    "freeform_creative": AITaskDefinition(
        id="freeform_creative",
        label="Freeform creative",
        description="User-provided creative prompt.",
        category=TaskCategory.GENERAL,
        local_acceptable=True,
        uses_selection=True,
        uses_context=True,
        max_tokens=2048,
    ),
}


def get_task_definition(task_id: str) -> AITaskDefinition | None:
    """Get task definition by id."""
    return AI_TASK_CATALOG.get(task_id)


def get_tasks_by_category(category: TaskCategory) -> list[AITaskDefinition]:
    """Get all tasks in a category."""
    return [t for t in AI_TASK_CATALOG.values() if t.category == category]


def list_task_ids() -> list[str]:
    """List all task IDs."""
    return list(AI_TASK_CATALOG.keys())
