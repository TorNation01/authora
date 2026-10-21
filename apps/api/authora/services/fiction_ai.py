"""Fiction AI service - build context and handle fiction-specific prompts."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    Book,
    Chapter,
    CharacterRelationship,
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
        if ws.logline:
            parts.append(f"LOGLINE: {ws.logline}")
        if ws.genre:
            parts.append(f"PRIMARY GENRE: {ws.genre}")
        if ws.subgenre:
            parts.append(f"SUBGENRE: {ws.subgenre}")
        if ws.genre_tags:
            parts.append(f"GENRE BLEND: {', '.join(ws.genre_tags)}")
        if ws.audience:
            parts.append(f"AUDIENCE: {ws.audience}")
        if ws.pov:
            parts.append(f"POINT OF VIEW: {ws.pov}")
        if ws.tense:
            parts.append(f"TENSE: {ws.tense}")
        if ws.target_word_count:
            parts.append(f"TARGET LENGTH: {ws.target_word_count} words")
        if ws.comparable_titles:
            parts.append(f"COMPARABLE TITLES: {', '.join(ws.comparable_titles)}")
        if ws.central_question:
            parts.append(f"CENTRAL DRAMATIC QUESTION: {ws.central_question}")
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
                line += f": {c.description[:200]}"
            details = []
            if c.age:
                details.append(f"age {c.age}")
            if c.goals:
                details.append(f"wants {c.goals[:160]}")
            if c.need:
                details.append(f"needs {c.need[:160]}")
            if c.wound:
                details.append(f"wound: {c.wound[:160]}")
            if c.flaws:
                details.append(f"flaw: {c.flaws[:160]}")
            if c.secret:
                details.append(f"secret: {c.secret[:160]}")
            if c.voice:
                details.append(f"voice: {c.voice[:120]}")
            if c.arc_summary:
                details.append(f"arc: {c.arc_summary[:200]}")
            if details:
                line += " | " + "; ".join(details)
            char_lines.append(line)
        parts.append("CHARACTERS:\n" + "\n".join(char_lines))

    # Relationships
    result = await db.execute(
        select(CharacterRelationship).where(CharacterRelationship.book_id == book_id)
    )
    rels = result.scalars().all()
    if rels:
        by_id = {c.id: c.name for c in chars}
        rel_lines = []
        for r in rels:
            a = by_id.get(r.character_a_id, "unknown")
            b = by_id.get(r.character_b_id, "unknown")
            rel_lines.append(f"- {a} is {r.relationship_type} of {b} (intensity {r.intensity}/5): {(r.description or '')[:140]}")
        parts.append("RELATIONSHIPS:\n" + "\n".join(rel_lines))

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
    # --- Book Bible: interrogation prompts. These are craft questions, not generic
    # "improve this" prompts; each one names the failure mode it is hunting for. ---
    "character_interrogate": (
        "You are a demanding developmental editor interviewing a character before the book is written. "
        "Using the character sheet in the context, answer as the character in first person, then step out of voice. "
        "Structure the response exactly like this:\n"
        "IN THEIR OWN WORDS — 150 words, first person, no summary.\n"
        "WHAT THEY WANT AND WHY IT IS NOT ENOUGH — 80 words.\n"
        "THE THING THEY WILL NOT SAY — one paragraph naming the secret or admission they are protecting.\n"
        "THREE QUESTIONS THE AUTHOR MUST ANSWER — a numbered list of three specific questions this character "
        "exposes in the book's premise. No generic advice."
    ),
    "character_contradiction": (
        "You are a story editor hunting for the contradiction that makes a character feel alive. "
        "Using the character sheet in the context, name the single strongest contradiction in this person: "
        "the want that fights the need, the virtue that is really a defence, the belief contradicted by their behaviour. "
        "Then explain in 120 words how that contradiction should show up in a scene, not in exposition. "
        "End with one line of dialogue this character would say that reveals the contradiction without stating it."
    ),
    "character_lie": (
        "You are a story editor. Using the character sheet in the context, identify the lie this character "
        "believes about themselves and the lie they tell other people. For each: state the lie in one sentence, "
        "name the scene type where it should be exposed, and write the moment of exposure in 100 words of prose. "
        "Then say what it costs them to keep believing it. Do not compliment the character."
    ),
    "arc_beats": (
        "You are a story editor breaking a character arc. Using the character sheet and existing arc beats in the context, "
        "propose exactly three new beats that would break or complicate this arc — not complete it comfortably. "
        "For each beat use this exact format:\n"
        "BEAT: <short label>\n"
        "WHAT CHANGES: <one sentence, a change in belief or allegiance, not an event>\n"
        "CHAPTER: <suggested chapter number or range>\n"
        "EMOTIONAL TURN: <the feeling they move from and to>\n"
        "Then add one line explaining what the three beats cost the character across the book."
    ),
    "premise_scope": (
        "You are a developmental editor deciding whether a premise can carry a novel. Using the premise, logline, "
        "central question and target length in the context, answer plainly and without encouragement:\n"
        "VERDICT: NOVEL / NOVELLA / SHORT STORY — one of these three, with a one-sentence reason.\n"
        "WHY IT MIGHT NOT HOLD A NOVEL — the two most likely failure points, specific to this premise.\n"
        "WHAT WOULD MAKE IT A NOVEL — the complication, stake or relationship that must exist and does not yet.\n"
        "FIRST THREE SCENES — three scenes that would prove the premise works, one line each."
    ),
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
