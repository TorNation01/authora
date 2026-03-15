"""Ghostwriter AI service - prompt orchestration for guided draft flow."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, GhostwriterWorkspace
from authora.services.ai import complete_sync
from authora.services.export import tiptap_to_plain_text
from authora.services.fiction_ai import build_fiction_context
from authora.services.nonfiction_ai import build_nonfiction_context


def _build_intake_context(ws: GhostwriterWorkspace) -> str:
    """Build context string from intake answers."""
    parts = []
    if ws.intake_answers:
        for k, v in ws.intake_answers.items():
            if v:
                parts.append(f"{k}: {v}")
    if ws.voice_tone:
        parts.append(f"Voice/tone: {ws.voice_tone}")
    if ws.target_audience:
        parts.append(f"Target audience: {ws.target_audience}")
    if ws.desired_outcome:
        parts.append(f"Desired outcome: {ws.desired_outcome}")
    return "\n".join(parts) if parts else "(no intake data)"


async def generate_outline(
    db: AsyncSession,
    book_id: UUID,
    book_type: str,
    workspace: GhostwriterWorkspace,
) -> dict[str, Any]:
    """Generate book outline from intake and workspace context."""
    intake_ctx = _build_intake_context(workspace)
    if book_type == "fiction":
        ws_ctx = await build_fiction_context(db, book_id, include_recent=False)
    elif book_type == "nonfiction":
        ws_ctx = await build_nonfiction_context(db, book_id, include_recent=False)
    else:
        ws_ctx = ""

    system = """You are a professional ghostwriter. Generate a clear, structured book outline.
Output valid JSON only, no markdown. Format: {"chapters": [{"title": "...", "summary": "..."}, ...]}
Include 6-12 chapters. Each summary should be 1-3 sentences."""

    user = f"""Create a book outline.

INTAKE:
{intake_ctx}

WORKSPACE CONTEXT:
{ws_ctx or "(none)"}

Return JSON: {{"chapters": [{{"title": "Chapter 1 Title", "summary": "What this chapter covers"}}, ...]}}"""

    result = await complete_sync(user, system, max_tokens=2048)
    # Parse JSON from result (may have leading/trailing text)
    import json
    import re
    match = re.search(r"\{[\s\S]*\}", result)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"chapters": [{"title": "Chapter 1", "summary": result[:200]}]}


async def generate_chapter_brief(
    db: AsyncSession,
    book_id: UUID,
    book_type: str,
    chapter: Chapter,
    workspace: GhostwriterWorkspace,
    outline_chapter: dict[str, Any] | None = None,
) -> str:
    """Generate chapter brief for ghostwriter draft."""
    intake_ctx = _build_intake_context(workspace)
    if book_type == "fiction":
        ws_ctx = await build_fiction_context(db, book_id, chapter_id=chapter.id, include_recent=False)
    elif book_type == "nonfiction":
        ws_ctx = await build_nonfiction_context(db, book_id, chapter_id=chapter.id, include_recent=False)
    else:
        ws_ctx = ""

    outline_info = ""
    if outline_chapter:
        outline_info = f"\nOutline for this chapter: {outline_chapter.get('title', '')} - {outline_chapter.get('summary', '')}"

    system = """You are a professional ghostwriter. Write a detailed chapter brief (200-400 words) that will guide the full draft.
Include: key points to cover, tone, structure, any specific elements to include. Be specific enough that another writer could draft from it."""

    user = f"""Write a chapter brief for: {chapter.title}

INTAKE:
{intake_ctx}
{outline_info}

WORKSPACE:
{ws_ctx or "(none)"}

Write the brief:"""

    return await complete_sync(user, system, max_tokens=1024)


async def generate_chapter_draft(
    db: AsyncSession,
    book_id: UUID,
    book_type: str,
    chapter: Chapter,
    workspace: GhostwriterWorkspace,
    brief_text: str,
) -> str:
    """Generate full chapter draft from brief."""
    intake_ctx = _build_intake_context(workspace)
    if book_type == "fiction":
        ws_ctx = await build_fiction_context(db, book_id, chapter_id=chapter.id, include_recent=True)
    elif book_type == "nonfiction":
        ws_ctx = await build_nonfiction_context(db, book_id, chapter_id=chapter.id, include_recent=True)
    else:
        ws_ctx = ""

    existing = ""
    if chapter.content:
        text = tiptap_to_plain_text(chapter.content)
        if text.strip():
            existing = f"\n\nEXISTING CONTENT (continue or replace as needed):\n{text[-1500:]}"

    system = """You are a professional ghostwriter. Write full, polished prose from the brief.
Match the voice and tone specified. Write 500-1500 words per chapter. Output plain text only, no markdown.
Clearly indicate this is AI-generated content when appropriate."""

    user = f"""Write a full chapter draft.

CHAPTER: {chapter.title}

BRIEF:
{brief_text}

INTAKE:
{intake_ctx}

WORKSPACE:
{ws_ctx or "(none)"}
{existing}

Write the full chapter:"""

    return await complete_sync(user, system, max_tokens=4096)


async def regenerate_section(
    db: AsyncSession,
    book_id: UUID,
    book_type: str,
    selection: str,
    feedback: str | None = None,
) -> str:
    """Regenerate a section, optionally with feedback."""
    if book_type == "fiction":
        ws_ctx = await build_fiction_context(db, book_id, include_recent=False)
    elif book_type == "nonfiction":
        ws_ctx = await build_nonfiction_context(db, book_id, include_recent=False)
    else:
        ws_ctx = ""

    feedback_line = f"\n\nAuthor feedback: {feedback}" if feedback else ""

    system = """You are a ghostwriter. Regenerate the given section. Match the surrounding style.
If feedback is provided, incorporate it. Output the new section only, no explanations."""

    user = f"""Regenerate this section:
---
{selection}
---
{feedback_line}

WORKSPACE: {ws_ctx or "(none)"}

New section:"""

    return await complete_sync(user, system, max_tokens=2048)


async def rewrite_with_feedback(
    db: AsyncSession,
    book_id: UUID,
    book_type: str,
    selection: str,
    feedback: str,
) -> str:
    """Rewrite content incorporating user feedback."""
    if book_type == "fiction":
        ws_ctx = await build_fiction_context(db, book_id, include_recent=False)
    elif book_type == "nonfiction":
        ws_ctx = await build_nonfiction_context(db, book_id, include_recent=False)
    else:
        ws_ctx = ""

    system = """You are a ghostwriter. Rewrite the selection incorporating the author's feedback exactly.
Preserve voice and tone. Output the rewritten text only."""

    user = f"""Rewrite this incorporating the feedback:

ORIGINAL:
{selection}

AUTHOR FEEDBACK: {feedback}

WORKSPACE: {ws_ctx or "(none)"}

Rewritten text:"""

    return await complete_sync(user, system, max_tokens=2048)
