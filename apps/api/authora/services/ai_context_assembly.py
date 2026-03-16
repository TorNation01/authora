"""
Context Assembly System - intelligent context for AI prompts.

Assembles: selection, section, chapter summary, manuscript context, project settings,
character/world/research notes, guidance mode, template/framework, style preferences,
user instruction. Keeps context efficient and relevant.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from authora.services.ai_orchestration import BookType


# Max chars for different context sections to avoid overload
MAX_SELECTION_CHARS = 4000
MAX_CHAPTER_CONTEXT_CHARS = 3000
MAX_RAG_CHUNK_CHARS = 800
MAX_RAG_TOTAL_CHARS = 4000
MAX_WORKSPACE_CONTEXT_CHARS = 6000


async def assemble_context(
    db: AsyncSession,
    *,
    selection: str = "",
    book_id: UUID,
    book_type: BookType,
    chapter_id: UUID | None = None,
    project_id: UUID | None = None,
    user_id: UUID | None = None,
    rag_query: str | None = None,
    include_recent_chapter: bool = True,
    include_workspace: bool = True,
    include_rag: bool = True,
    guidance_mode: str | None = None,
    template_slug: str | None = None,
    style_preferences: dict | None = None,
    user_instruction: str | None = None,
) -> str:
    """
    Assemble efficient, relevant context for AI prompts.

    Rules:
    - Do not overload; use summaries when needed
    - Prioritize relevance
    - Distinguish creative vs factual context
    - Source-linked research clearly marked
    """
    parts: list[str] = []

    # 1. User instruction (highest priority)
    if user_instruction and user_instruction.strip():
        parts.append(f"USER REQUEST:\n{user_instruction.strip()[:2000]}")

    # 2. Selected text (truncated if needed)
    if selection and selection.strip():
        sel = selection.strip()
        if len(sel) > MAX_SELECTION_CHARS:
            sel = sel[:MAX_SELECTION_CHARS] + "\n[... truncated ...]"
        parts.append(f"SELECTED TEXT:\n{sel}")

    # 3. Workspace context (fiction/nonfiction/general)
    if include_workspace:
        workspace = await _build_workspace_context(
            db,
            book_id=book_id,
            book_type=book_type,
            chapter_id=chapter_id,
            include_recent=include_recent_chapter,
            max_chars=MAX_WORKSPACE_CONTEXT_CHARS,
        )
        if workspace:
            parts.append(f"WORKSPACE CONTEXT:\n{workspace}")

    # 4. RAG-retrieved context (if query and embeddings enabled)
    if include_rag and rag_query and project_id and user_id:
        rag_ctx = await _build_rag_context(
            db,
            project_id=project_id,
            book_id=book_id,
            user_id=user_id,
            query=rag_query,
            max_total_chars=MAX_RAG_TOTAL_CHARS,
        )
        if rag_ctx:
            parts.append(f"RELEVANT CONTENT FROM PROJECT (retrieved):\n{rag_ctx}")

    # 5. Project metadata (guidance mode, template) - compact
    meta_parts: list[str] = []
    if guidance_mode:
        meta_parts.append(f"Guidance mode: {guidance_mode}")
    if template_slug:
        meta_parts.append(f"Template: {template_slug}")
    if meta_parts:
        parts.append("PROJECT: " + "; ".join(meta_parts))

    # 6. Style preferences (if any)
    if style_preferences and isinstance(style_preferences, dict):
        prefs = style_preferences.get("voice") or style_preferences.get("tone")
        if prefs:
            parts.append(f"STYLE PREFERENCE: {prefs}")

    return "\n\n---\n\n".join(p for p in parts if p)


async def _build_workspace_context(
    db: AsyncSession,
    *,
    book_id: UUID,
    book_type: BookType,
    chapter_id: UUID | None = None,
    include_recent: bool = True,
    max_chars: int = MAX_WORKSPACE_CONTEXT_CHARS,
) -> str:
    """Build workspace context (fiction/nonfiction/general)."""
    from authora.services.ai_orchestration import build_workspace_context

    full = await build_workspace_context(
        db,
        book_id=book_id,
        book_type=book_type,
        chapter_id=chapter_id,
        include_recent=include_recent,
        project_id=None,
        rag_query=None,
        user_id=None,
    )
    if len(full) > max_chars:
        return full[-max_chars:] + "\n[... earlier context truncated ...]"
    return full


async def _build_rag_context(
    db: AsyncSession,
    *,
    project_id: UUID,
    book_id: UUID,
    user_id: UUID,
    query: str,
    max_total_chars: int = MAX_RAG_TOTAL_CHARS,
) -> str:
    """Build RAG context with source markers."""
    from authora.config import get_settings
    from authora.services.embedding_service import is_embeddings_configured
    from authora.services.rag import semantic_search

    if not is_embeddings_configured():
        return ""

    settings = get_settings()
    limit = getattr(settings, "rag_max_chunks", 5)
    from authora.services.hardware_model_mapping import get_rag_limits_for_tier
    from authora.services.hardware_tier import get_hardware_tier

    if settings.ollama_enabled:
        profile = get_hardware_tier(getattr(settings, "ollama_hardware_tier", None))
        tier_limits = get_rag_limits_for_tier(profile.tier)
        limit = tier_limits.get("rag_max_chunks", limit)

    chunks = await semantic_search(
        db, project_id, query,
        user_id=user_id, book_id=book_id,
        limit=limit,
    )
    if not chunks:
        return ""

    parts: list[str] = []
    total = 0
    for r in chunks:
        text = (r.content_text or "")[:MAX_RAG_CHUNK_CHARS]
        if len(r.content_text or "") > MAX_RAG_CHUNK_CHARS:
            text += "..."
        source = f"[{r.source_type}]"
        parts.append(f"{source} {text}")
        total += len(text)
        if total >= max_total_chars:
            break

    return "\n\n".join(parts)
