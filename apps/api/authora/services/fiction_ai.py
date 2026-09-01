"""Fiction AI service - build context and handle fiction-specific prompts."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    Book,
    Chapter,
    FictionCharacter,
    FictionTracker,
    FictionWorkspace,
    PlotArc,
    Scene,
    WorldElement,
)
from authora.services.ai_registry import TASK_FICTION_IDEATION
from authora.services.ai_service import complete_stream
from authora.services.export import tiptap_to_plain_text


async def build_fiction_context(
    db: AsyncSession,
    book_id: UUID,
    chapter_id: UUID | None = None,
    scene_id: UUID | None = None,
    include_recent: bool = True,
) -> str:
    """Build context string from fiction workspace for AI prompts."""
    parts = []

    # Workspace
    result = await db.execute(select(FictionWorkspace).where(FictionWorkspace.book_id == book_id))
    ws = result.scalar_one_or_none()
    if ws:
        if ws.premise:
            parts.append(f"PREMISE: {ws.premise}")
        if ws.genre:
            parts.append(f"PRIMARY GENRE: {ws.genre}")
        if ws.genre_tags:
            parts.append(f"GENRE BLEND: {', '.join(ws.genre_tags)}")
        if ws.tone:
            parts.append(f"TONE: {ws.tone}")
        if ws.themes:
            parts.append(f"THEMES: {', '.join(ws.themes)}")
        if ws.pacing_notes:
            parts.append(f"PACING: {ws.pacing_notes}")

    # Characters
    result = await db.execute(
        select(FictionCharacter).where(FictionCharacter.book_id == book_id).order_by(FictionCharacter.sort_order)
    )
    chars = result.scalars().all()
    if chars:
        char_lines = []
        for c in chars:
            line = f"- {c.name} ({c.role})"
            if c.description:
                line += f": {c.description[:200]}..."
            char_lines.append(line)
        parts.append("CHARACTERS:\n" + "\n".join(char_lines))

    # World elements
    result = await db.execute(
        select(WorldElement).where(WorldElement.book_id == book_id).order_by(WorldElement.sort_order)
    )
    world = result.scalars().all()
    if world:
        world_lines = [f"- {w.name} ({w.category}): {w.description[:150]}..." if w.description else f"- {w.name} ({w.category})" for w in world[:10]]
        parts.append("WORLD:\n" + "\n".join(world_lines))

    # Plot arcs
    result = await db.execute(select(PlotArc).where(PlotArc.book_id == book_id).order_by(PlotArc.sort_order))
    arcs = result.scalars().all()
    if arcs:
        arc_lines = [f"- {a.name} ({a.structure})" for a in arcs]
        parts.append("PLOT ARCS:\n" + "\n".join(arc_lines))

    # Scenes
    result = await db.execute(select(Scene).where(Scene.book_id == book_id).order_by(Scene.sort_order))
    scenes = result.scalars().all()
    if scenes:
        scene_lines = [f"- {s.title}: {s.summary[:100]}..." if s.summary else f"- {s.title}" for s in scenes[:15]]
        parts.append("SCENES:\n" + "\n".join(scene_lines))

    # Unresolved threads
    result = await db.execute(
        select(FictionTracker).where(
            FictionTracker.book_id == book_id,
            FictionTracker.type == "unresolved",
            FictionTracker.status == "pending",
        )
    )
    unresolved = result.scalars().all()
    if unresolved:
        parts.append("UNRESOLVED THREADS:\n" + "\n".join(f"- {t.title}" for t in unresolved))

    # Recent chapter content
    if include_recent and chapter_id:
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
        ch = result.scalar_one_or_none()
        if ch and ch.content:
            text = tiptap_to_plain_text(ch.content)
            if text:
                parts.append(f"CURRENT CHAPTER (last ~2000 chars):\n{text[-2000:]}")

    return "\n\n".join(parts) if parts else "No fiction context available."


FICTION_PROMPT_TEMPLATES = {
    "alternate_scenes": "Generate 3 alternate scene ideas for what could happen next. Each should be 2-3 sentences. Be creative and varied.",
    "improve_dialogue": "Improve this dialogue to sound more natural and character-appropriate. Keep the same meaning and intent:\n\n{selection}",
    "deepen_emotion": "Deepen the emotional resonance of this passage. Add sensory details and interiority without changing the plot:\n\n{selection}",
    "increase_tension": "Rewrite this passage to increase tension and pacing. Keep the same events but make it more gripping:\n\n{selection}",
    "fix_pacing": "This passage feels too slow/fast. Suggest a revised version with better pacing:\n\n{selection}",
    "rewrite_pov": "Rewrite this scene from {pov} point of view. Keep the same events but filter through their perspective:\n\n{selection}",
    "suggest_twists": "Suggest 3 plot twists that could work for this story. Each should be 2-3 sentences and feel earned.",
    "identify_weak": "Identify the 3 weakest aspects of this chapter (pacing, dialogue, description, tension, etc.) and suggest specific improvements for each.",
    "chapter_summary": "Write a concise chapter summary (1-2 paragraphs) capturing the key events, character beats, and any setup or payoff.",
    "scene_ideas": "Generate 5 scene ideas that could work for this story. Each should be 1-2 sentences and fit the premise and tone.",
    "what_happens_next": "Suggest 3 compelling directions for what could happen next in this story. Each should be 2-3 sentences.",
    "dialogue_helper": "Help me write dialogue for this situation. The characters are {characters}. The context is: {context}",
}


async def run_fiction_ai_prompt(
    db: AsyncSession,
    book_id: UUID,
    chapter_id: UUID | None,
    prompt_type: str,
    context: str | None = None,
    selection: str | None = None,
    scene_id: UUID | None = None,
) -> str:
    """Run a fiction-specific AI prompt and return the result."""
    system = await build_fiction_context(db, book_id, chapter_id, scene_id, include_recent=bool(chapter_id))

    template = FICTION_PROMPT_TEMPLATES.get(prompt_type)
    if not template:
        return f"Unknown prompt type: {prompt_type}"

    format_kw = {"selection": selection or "", "pov": "another character's", "characters": "the main characters", "context": context or ""}
    try:
        user_prompt = template.format(**format_kw)
    except KeyError:
        user_prompt = template
    if context and "{context}" not in template and "{selection}" not in template:
        user_prompt = f"{user_prompt}\n\n{context}"

    result = []
    async for chunk in complete_stream(
        user_prompt, system, max_tokens=2048, task=TASK_FICTION_IDEATION
    ):
        result.append(chunk)
    return "".join(result)
