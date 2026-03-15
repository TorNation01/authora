"""Non-fiction AI service - build context and handle non-fiction prompts."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    ArgumentStructure,
    AuthorityBuilder,
    Book,
    CaseStudy,
    Chapter,
    NFChapterPlan,
    NFResearchNote,
    NonfictionWorkspace,
    SupportingExample,
    SummaryActionStep,
    TargetAudience,
    TransformationFramework,
)
from authora.services.export import tiptap_to_plain_text


async def build_nonfiction_context(
    db: AsyncSession,
    book_id: UUID,
    chapter_id: UUID | None = None,
    include_recent: bool = True,
) -> str:
    """Build context string from non-fiction workspace for AI prompts."""
    parts = []

    result = await db.execute(select(NonfictionWorkspace).where(NonfictionWorkspace.book_id == book_id))
    ws = result.scalar_one_or_none()
    if ws:
        if ws.core_message:
            parts.append(f"CORE MESSAGE: {ws.core_message}")
        if ws.reader_outcome:
            parts.append(f"READER OUTCOME: {ws.reader_outcome}")
        if ws.reader_promise:
            parts.append(f"READER PROMISE: {ws.reader_promise}")
        if ws.topic:
            parts.append(f"TOPIC: {ws.topic}")

    result = await db.execute(select(TargetAudience).where(TargetAudience.book_id == book_id).order_by(TargetAudience.sort_order))
    audiences = result.scalars().all()
    if audiences:
        a = audiences[0]
        lines = []
        if a.demographics:
            lines.append(f"Demographics: {a.demographics[:200]}...")
        if a.pain_points:
            lines.append(f"Pain points: {a.pain_points[:200]}...")
        if a.goals:
            lines.append(f"Goals: {a.goals[:200]}...")
        if lines:
            parts.append("TARGET AUDIENCE:\n" + "\n".join(lines))

    result = await db.execute(select(TransformationFramework).where(TransformationFramework.book_id == book_id).order_by(TransformationFramework.sort_order))
    transforms = result.scalars().all()
    if transforms:
        t = transforms[0]
        lines = []
        if t.before_state:
            lines.append(f"Before: {t.before_state[:150]}...")
        if t.after_state:
            lines.append(f"After: {t.after_state[:150]}...")
        if lines:
            parts.append("TRANSFORMATION:\n" + "\n".join(lines))

    result = await db.execute(select(NFChapterPlan).where(NFChapterPlan.book_id == book_id).order_by(NFChapterPlan.sort_order))
    plans = result.scalars().all()
    if plans:
        lines = [f"- {p.title}: {p.summary[:80]}..." if p.summary else f"- {p.title}" for p in plans[:10]]
        parts.append("CHAPTER FRAMEWORK:\n" + "\n".join(lines))

    result = await db.execute(select(ArgumentStructure).where(ArgumentStructure.book_id == book_id).order_by(ArgumentStructure.sort_order))
    args = result.scalars().all()
    if args:
        lines = [f"- {a.main_argument[:80]}..." if a.main_argument else "- (argument)" for a in args[:5]]
        parts.append("ARGUMENTS:\n" + "\n".join(lines))

    if include_recent and chapter_id:
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
        ch = result.scalar_one_or_none()
        if ch and ch.content:
            text = tiptap_to_plain_text(ch.content)
            if text:
                parts.append(f"CURRENT CHAPTER (last ~2000 chars):\n{text[-2000:]}")

    return "\n\n".join(parts) if parts else "No non-fiction context available."


NONFICTION_PROMPT_TEMPLATES = {
    "clarify_message": "Clarify and sharpen this core message. Make it more concise and impactful:\n\n{selection}",
    "improve_structure": "Improve the structure of this section. Suggest better organization and flow:\n\n{selection}",
    "simplify_explanations": "Simplify this explanation so it's easier for a general audience to understand:\n\n{selection}",
    "strengthen_persuasiveness": "Strengthen the persuasiveness of this argument. Add evidence and logical flow:\n\n{selection}",
    "create_outlines": "Create a detailed outline for this content. Include main points and sub-points.",
    "expand_sections": "Expand this section with more detail, examples, and explanation:\n\n{selection}",
    "tone_professional": "Rewrite this passage in a more professional tone:\n\n{selection}",
    "tone_friendly": "Rewrite this passage in a warmer, more friendly tone:\n\n{selection}",
    "tone_accessible": "Rewrite this passage to be more accessible and engaging for a general audience:\n\n{selection}",
    "create_examples": "Create 2-3 concrete examples that illustrate this concept:\n\n{selection}",
    "create_analogies": "Create 2-3 analogies that help explain this concept:\n\n{selection}",
    "summarize_complex": "Summarize this complex material in a clear, accessible way:\n\n{selection}",
}
