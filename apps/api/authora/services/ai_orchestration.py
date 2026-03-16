"""AI prompt orchestration - modes, actions, templates."""

from dataclasses import dataclass
from enum import Enum

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class AIMode(str, Enum):
    """AI assistance mode - affects creativity and preservation of voice."""

    ASSIST = "assist"  # Light suggestions, preserve voice
    CO_WRITE = "co_write"  # Collaborative, moderate changes
    GHOSTWRITER = "ghostwriter"  # Full generation from brief
    EDIT = "editing"  # Improve existing text, minimal creativity (alias: editing)
    SPARK = "spark"  # Creative brainstorming, idea generation
    IDEA_GENERATION = "idea_generation"  # Alias for SPARK (legacy)


class AssistanceLevel(str, Enum):
    """How much AI can change the text."""

    STRICT = "strict"  # Minimal changes, preserve exactly
    MODERATE = "moderate"  # Balanced
    CREATIVE = "creative"  # More freedom to reimagine


class BookType(str, Enum):
    FICTION = "fiction"
    NONFICTION = "nonfiction"
    GENERAL = "general"


@dataclass
class ActionDefinition:
    """Definition of an AI action."""

    id: str
    label: str
    description: str
    fiction_prompt: str
    nonfiction_prompt: str
    general_prompt: str
    uses_selection: bool = True
    uses_context: bool = True
    max_tokens: int = 1024


# All AI actions with fiction/nonfiction/general variants
ACTION_DEFINITIONS: dict[str, ActionDefinition] = {
    "rewrite_sentence": ActionDefinition(
        id="rewrite_sentence",
        label="Rewrite sentence",
        description="Rewrite the selected sentence for clarity or style.",
        fiction_prompt="Rewrite this sentence to improve flow and style. Preserve the author's voice and meaning:\n\n{selection}",
        nonfiction_prompt="Rewrite this sentence for clarity and impact. Keep the same meaning:\n\n{selection}",
        general_prompt="Rewrite this sentence for clarity and style:\n\n{selection}",
    ),
    "rewrite_paragraph": ActionDefinition(
        id="rewrite_paragraph",
        label="Rewrite paragraph",
        description="Rewrite the selected paragraph.",
        fiction_prompt="Rewrite this paragraph. Improve flow and engagement while preserving the author's voice:\n\n{selection}",
        nonfiction_prompt="Rewrite this paragraph for clarity and logical flow:\n\n{selection}",
        general_prompt="Rewrite this paragraph for clarity and flow:\n\n{selection}",
    ),
    "improve_wording": ActionDefinition(
        id="improve_wording",
        label="Improve wording",
        description="Suggest better word choices.",
        fiction_prompt="Improve the wording of this passage. Suggest more vivid or precise alternatives while keeping the author's style:\n\n{selection}",
        nonfiction_prompt="Improve the wording for precision and impact:\n\n{selection}",
        general_prompt="Improve the wording of this passage:\n\n{selection}",
    ),
    "improve_flow": ActionDefinition(
        id="improve_flow",
        label="Improve flow",
        description="Improve transitions and readability.",
        fiction_prompt="Improve the flow of this passage. Fix awkward transitions and pacing:\n\n{selection}",
        nonfiction_prompt="Improve the flow and logical progression of this section:\n\n{selection}",
        general_prompt="Improve the flow of this passage:\n\n{selection}",
    ),
    "expand": ActionDefinition(
        id="expand",
        label="Expand",
        description="Expand with more detail.",
        fiction_prompt="Expand this passage with more sensory detail, dialogue, or description. Stay true to the scene:\n\n{selection}",
        nonfiction_prompt="Expand this section with more explanation, examples, or evidence:\n\n{selection}",
        general_prompt="Expand this passage with more detail:\n\n{selection}",
    ),
    "condense": ActionDefinition(
        id="condense",
        label="Condense",
        description="Make more concise.",
        fiction_prompt="Condense this passage. Keep the essential beats and emotion, remove redundancy:\n\n{selection}",
        nonfiction_prompt="Condense this section. Keep key points, remove redundancy:\n\n{selection}",
        general_prompt="Condense this passage while preserving meaning:\n\n{selection}",
    ),
    "change_tone": ActionDefinition(
        id="change_tone",
        label="Change tone",
        description="Change tone (e.g. formal, casual).",
        fiction_prompt="Rewrite this passage in a {tone} tone. Keep the same events and meaning:\n\n{selection}",
        nonfiction_prompt="Rewrite this passage in a {tone} tone:\n\n{selection}",
        general_prompt="Rewrite in a {tone} tone:\n\n{selection}",
        uses_selection=True,
    ),
    "continue_draft": ActionDefinition(
        id="continue_draft",
        label="Continue draft",
        description="Continue from where the text ends.",
        fiction_prompt="Continue this draft in the same voice and style. Write the next 2-4 paragraphs:\n\n{selection}",
        nonfiction_prompt="Continue this section. Maintain the argument and tone:\n\n{selection}",
        general_prompt="Continue this draft in the same style:\n\n{selection}",
        uses_selection=True,
        max_tokens=2048,
    ),
    "generate_outline": ActionDefinition(
        id="generate_outline",
        label="Generate outline",
        description="Generate an outline from context.",
        fiction_prompt="Generate a chapter outline based on this premise and context. Include scene beats:\n\n{context}",
        nonfiction_prompt="Generate a detailed outline for this topic. Include main points and sub-points:\n\n{context}",
        general_prompt="Generate an outline based on this context:\n\n{context}",
        uses_selection=False,
        uses_context=True,
        max_tokens=1024,
    ),
    "generate_scene_ideas": ActionDefinition(
        id="generate_scene_ideas",
        label="Generate scene ideas",
        description="Generate scene ideas.",
        fiction_prompt="Generate 5 scene ideas that could work for this story. Each 1-2 sentences:\n\n{context}",
        nonfiction_prompt="Generate 5 section ideas for this chapter:\n\n{context}",
        general_prompt="Generate 5 ideas for what could come next:\n\n{context}",
        uses_selection=False,
        max_tokens=1024,
    ),
    "generate_chapter_ideas": ActionDefinition(
        id="generate_chapter_ideas",
        label="Generate chapter ideas",
        description="Generate chapter-level ideas and directions.",
        fiction_prompt="Generate 5 chapter ideas or directions for this book. Each 2-3 sentences with a clear premise:\n\n{context}",
        nonfiction_prompt="Generate 5 chapter ideas for this topic. Each 2-3 sentences with main focus:\n\n{context}",
        general_prompt="Generate 5 chapter ideas based on this context:\n\n{context}",
        uses_selection=False,
        uses_context=True,
        max_tokens=1024,
    ),
    "generate_examples": ActionDefinition(
        id="generate_examples",
        label="Generate examples",
        description="Generate illustrative examples.",
        fiction_prompt="Generate 2-3 concrete examples or scenarios that illustrate this concept:\n\n{selection}",
        nonfiction_prompt="Generate 2-3 concrete examples that illustrate this concept:\n\n{selection}",
        general_prompt="Generate 2-3 examples:\n\n{selection}",
    ),
    "summarize_chapter": ActionDefinition(
        id="summarize_chapter",
        label="Summarize chapter",
        description="Summarize the chapter.",
        fiction_prompt="Write a concise chapter summary (1-2 paragraphs) capturing key events and character beats:\n\n{selection}",
        nonfiction_prompt="Summarize this chapter in 1-2 paragraphs. Capture the main argument and key points:\n\n{selection}",
        general_prompt="Summarize this chapter:\n\n{selection}",
        max_tokens=512,
    ),
    "suggest_chapter_names": ActionDefinition(
        id="suggest_chapter_names",
        label="Suggest chapter names",
        description="Suggest chapter title options.",
        fiction_prompt="Suggest 5 chapter title options that fit this content. Mix evocative and literal:\n\n{selection}",
        nonfiction_prompt="Suggest 5 chapter title options that capture the content:\n\n{selection}",
        general_prompt="Suggest 5 chapter title options:\n\n{selection}",
        max_tokens=256,
    ),
    "fix_transitions": ActionDefinition(
        id="fix_transitions",
        label="Fix transitions",
        description="Improve transitions between sections.",
        fiction_prompt="Improve the transitions in this passage. Make the flow between ideas smoother:\n\n{selection}",
        nonfiction_prompt="Improve transitions between these sections for logical flow:\n\n{selection}",
        general_prompt="Fix transitions in this passage:\n\n{selection}",
    ),
    "create_hook": ActionDefinition(
        id="create_hook",
        label="Create hook/opening",
        description="Create an engaging opening.",
        fiction_prompt="Write 2-3 opening hook options for this chapter. Each should grab the reader:\n\n{context}",
        nonfiction_prompt="Write 2-3 opening hook options that draw the reader in:\n\n{context}",
        general_prompt="Create 2-3 opening hooks:\n\n{context}",
        uses_selection=False,
        max_tokens=512,
    ),
    "create_conclusion": ActionDefinition(
        id="create_conclusion",
        label="Create conclusion",
        description="Create a strong conclusion.",
        fiction_prompt="Write 2-3 conclusion options that satisfyingly close this chapter:\n\n{selection}",
        nonfiction_prompt="Write 2-3 conclusion options that reinforce the main message:\n\n{selection}",
        general_prompt="Create 2-3 conclusion options:\n\n{selection}",
    ),
    "help_when_stuck": ActionDefinition(
        id="help_when_stuck",
        label="Help when stuck",
        description="Get unstuck with suggestions.",
        fiction_prompt="The author is stuck here. Suggest 3 different directions they could take next. Be encouraging:\n\n{selection}",
        nonfiction_prompt="The author is stuck. Suggest 3 ways to develop this section further:\n\n{selection}",
        general_prompt="Suggest 3 directions to continue:\n\n{selection}",
        max_tokens=1024,
    ),
    "notes_to_prose": ActionDefinition(
        id="notes_to_prose",
        label="Convert notes to prose",
        description="Convert rough notes into polished prose.",
        fiction_prompt="Convert these rough notes into polished prose. Maintain a narrative voice:\n\n{selection}",
        nonfiction_prompt="Convert these notes into clear, structured prose:\n\n{selection}",
        general_prompt="Convert these notes into polished prose:\n\n{selection}",
        max_tokens=2048,
    ),
    "generate_section": ActionDefinition(
        id="generate_section",
        label="Generate full section",
        description="Generate a full section from guided inputs.",
        fiction_prompt="Generate a full section based on these guidelines. Write 3-5 paragraphs:\n\n{context}",
        nonfiction_prompt="Generate a full section based on these guidelines. Write 3-5 paragraphs:\n\n{context}",
        general_prompt="Generate a section based on:\n\n{context}",
        uses_selection=False,
        uses_context=True,
        max_tokens=2048,
    ),
}


MODE_SYSTEM_PREFIXES = {
    AIMode.ASSIST: "You are a supportive writing assistant. Make light suggestions. Preserve the author's voice and choices. Clearly indicate this is a suggestion.",
    AIMode.CO_WRITE: "You are a collaborative writing partner. You may suggest moderate changes. Preserve the author's core voice while offering improvements. Mark AI-generated content clearly.",
    AIMode.GHOSTWRITER: "You are a ghostwriter. Generate full prose from the author's brief. Match their stated style and voice. Clearly mark all AI-generated content.",
    AIMode.EDIT: "You are an editor. Improve the text with minimal creative changes. Fix grammar, flow, and clarity. Preserve the author's exact meaning and voice.",
    AIMode.SPARK: "You are a creative brainstorming partner. Generate varied, imaginative ideas. Quantity and variety over polish. Clearly separate each idea.",
    AIMode.IDEA_GENERATION: "You are a creative brainstorming partner. Generate varied, imaginative ideas. Quantity and variety over polish. Clearly separate each idea.",
}

ASSISTANCE_LEVEL_HINTS = {
    AssistanceLevel.STRICT: "Make minimal changes. Preserve the author's exact wording where possible.",
    AssistanceLevel.MODERATE: "Balance improvement with preservation of the author's voice.",
    AssistanceLevel.CREATIVE: "You may reimagine and expand. Stay true to the author's intent.",
}


async def build_workspace_context(
    db: AsyncSession,
    book_id: UUID,
    book_type: BookType,
    chapter_id: UUID | None = None,
    include_recent: bool = True,
    project_id: UUID | None = None,
    rag_query: str | None = None,
    user_id: UUID | None = None,
) -> str:
    """Build workspace context for AI prompts. Optionally augments with RAG-retrieved chunks."""
    parts: list[str] = []
    if book_type == BookType.FICTION:
        from authora.services.fiction_ai import build_fiction_context

        parts.append(await build_fiction_context(
            db, book_id, chapter_id, include_recent=include_recent
        ))
    elif book_type == BookType.NONFICTION:
        from authora.services.nonfiction_ai import build_nonfiction_context

        parts.append(await build_nonfiction_context(
            db, book_id, chapter_id, include_recent=include_recent
        ))
    elif chapter_id and include_recent:
        from sqlalchemy import select

        from authora.models import Chapter
        from authora.services.export import tiptap_to_plain_text

        result = await db.execute(
            select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
        )
        ch = result.scalar_one_or_none()
        if ch and ch.content:
            text = tiptap_to_plain_text(ch.content)
            if text:
                parts.append(f"CURRENT CHAPTER (last ~2000 chars):\n{text[-2000:]}")

    if rag_query and project_id and user_id:
        from authora.config import get_settings
        from authora.services.embedding_service import is_embeddings_configured
        from authora.services.rag import semantic_search

        s = get_settings()
        if is_embeddings_configured():
            from authora.services.hardware_model_mapping import get_rag_limits_for_tier
            from authora.services.hardware_tier import get_hardware_tier

            limit = s.rag_max_chunks
            if s.ollama_enabled:
                profile = get_hardware_tier(getattr(s, "ollama_hardware_tier", None))
                tier_limits = get_rag_limits_for_tier(profile.tier)
                limit = tier_limits.get("rag_max_chunks", limit)
            chunks = await semantic_search(
                db, project_id, rag_query,
                user_id=user_id, book_id=book_id,
                limit=limit,
            )
            if chunks:
                rag_text = "\n\n---\n\n".join(
                    f"[{r.source_type}] {r.content_text[:800]}{'...' if len(r.content_text) > 800 else ''}"
                    for r in chunks
                )
                parts.append(f"RELEVANT CONTEXT FROM YOUR PROJECT:\n{rag_text}")

    return "\n\n".join(p for p in parts if p)


def get_action_definition(action_id: str) -> ActionDefinition | None:
    """Get action definition by id."""
    return ACTION_DEFINITIONS.get(action_id)


def build_user_prompt(
    action_id: str,
    book_type: BookType,
    selection: str = "",
    context: str = "",
    extra: dict[str, str] | None = None,
) -> str:
    """Build user prompt for an action."""
    action = get_action_definition(action_id)
    if not action:
        return ""

    if book_type == BookType.FICTION:
        template = action.fiction_prompt
    elif book_type == BookType.NONFICTION:
        template = action.nonfiction_prompt
    else:
        template = action.general_prompt

    fmt = {
        "selection": selection or "(no selection)",
        "context": context or "(no context)",
        "tone": (extra or {}).get("tone", "professional"),
    }
    if extra:
        fmt.update(extra)
    try:
        return template.format(**fmt)
    except KeyError:
        return template


def build_system_prompt(
    mode: AIMode,
    level: AssistanceLevel,
    book_type: BookType,
    workspace_context: str = "",
) -> str:
    """Build system prompt from mode, level, and context."""
    parts = [MODE_SYSTEM_PREFIXES.get(mode, MODE_SYSTEM_PREFIXES[AIMode.ASSIST])]
    parts.append(ASSISTANCE_LEVEL_HINTS.get(level, ASSISTANCE_LEVEL_HINTS[AssistanceLevel.MODERATE]))
    parts.append("Always clearly indicate AI-generated content when suggesting changes.")
    if book_type == BookType.FICTION:
        parts.append("This is fiction. Consider narrative, character voice, and pacing.")
    elif book_type == BookType.NONFICTION:
        parts.append("This is non-fiction. Prioritize clarity, logic, and evidence.")
    if workspace_context:
        parts.append(f"\n\nWorkspace context:\n{workspace_context}")
    return "\n\n".join(parts)
