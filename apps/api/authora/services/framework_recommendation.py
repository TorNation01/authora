"""Framework recommendation engine.

Recommends writing frameworks based on project type, genre, template,
and user preferences.
"""

from typing import Any

# Map template structure_framework values to writing_frameworks slugs
_TEMPLATE_FRAMEWORK_MAP = {
    "emotional_arc": "memoir_lesson",
    "module_exercise": "workbook",
    "prompt_based": "workbook",
    "section_sequence": "custom_fiction",
    "collection_sequence": "custom_fiction",
    "client_workflow": "custom_nonfiction",
}


def _map_template_framework_to_slug(template_framework: str) -> str:
    """Map template structure_framework to writing_frameworks slug."""
    return _TEMPLATE_FRAMEWORK_MAP.get(template_framework, template_framework)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import ProjectTemplate, WritingFramework


async def recommend_frameworks(
    db: AsyncSession,
    *,
    book_type: str,
    genre: str | None = None,
    genre_tags: list[str] | None = None,
    template_id: UUID | None = None,
    template_slug: str | None = None,
    is_series: bool = False,
    limit: int = 5,
) -> list[WritingFramework]:
    """Recommend frameworks for a book based on type, genre blend, and template."""
    q = (
        select(WritingFramework)
        .where(
            WritingFramework.book_type == book_type,
            WritingFramework.is_disabled.is_(False),
        )
        .order_by(WritingFramework.sort_order.asc())
    )
    result = await db.execute(q)
    all_frameworks = result.scalars().all()

    scored: list[tuple[WritingFramework, float]] = []
    # Build search set: primary genre + all genre tags
    search_terms: list[str] = []
    if genre:
        search_terms.append(genre.lower())
    if genre_tags:
        search_terms.extend(t.lower() for t in genre_tags)
    search_terms = list(dict.fromkeys(search_terms))  # dedupe, preserve order
    template_slug_resolved = template_slug

    if template_id and not template_slug_resolved:
        t = await db.get(ProjectTemplate, template_id)
        if t:
            template_slug_resolved = t.slug

    for fw in all_frameworks:
        score = 0.5
        rules = fw.recommendation_rules or {}

        ideal_genres = rules.get("ideal_genres") or rules.get("genres") or fw.ideal_genres or []
        for g in ideal_genres:
            g_lower = g.lower()
            for term in search_terms:
                if g_lower in term or term in g_lower:
                    score += rules.get("weight", 0.5)
                    break
            else:
                continue
            break
        if not search_terms and ideal_genres:
            score += 0.2

        weight = rules.get("weight", 0.5)
        if weight > 0.8:
            score += 0.2
        if fw.is_featured:
            score += 0.15
        if rules.get("launch_priority"):
            score += 0.25

        if is_series and fw.slug == "series_arc":
            score += 0.5

        if template_slug_resolved:
            if "romance" in template_slug_resolved and fw.slug == "romance_beats":
                score += 0.5
            if "thriller" in template_slug_resolved or "mystery" in template_slug_resolved:
                if fw.slug == "mystery_thriller":
                    score += 0.5
            if "fantasy" in template_slug_resolved or "scifi" in template_slug_resolved:
                if fw.slug == "hero_journey":
                    score += 0.3
            if "memoir" in template_slug_resolved and fw.slug == "memoir_lesson":
                score += 0.5
            if "workbook" in template_slug_resolved and fw.slug == "workbook":
                score += 0.5
            if "selfhelp" in template_slug_resolved and fw.slug == "step_by_step":
                score += 0.3
            if "business" in template_slug_resolved and fw.slug == "authority":
                score += 0.5

        scored.append((fw, score))

    scored.sort(key=lambda x: -x[1])
    return [fw for fw, _ in scored[:limit]]


async def get_framework_by_slug(db: AsyncSession, slug: str) -> WritingFramework | None:
    """Get framework by slug."""
    result = await db.execute(
        select(WritingFramework).where(
            WritingFramework.slug == slug,
            WritingFramework.is_disabled.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def get_framework_for_template(
    db: AsyncSession,
    template: ProjectTemplate,
    structure_framework: str | None = None,
) -> WritingFramework | None:
    """Resolve framework from template and optional structure_framework override."""
    if structure_framework:
        slug = _map_template_framework_to_slug(structure_framework)
        fw = await get_framework_by_slug(db, slug)
        if fw:
            return fw

    template_framework = template.structure_framework if template else None
    if template_framework:
        slug = _map_template_framework_to_slug(template_framework)
        return await get_framework_by_slug(db, slug)

    book_type = template.book_type if template else "fiction"
    genre = template.genre
    genre_tags = template.genre_tags if template else None
    recs = await recommend_frameworks(
        db,
        book_type=book_type,
        genre=genre,
        genre_tags=genre_tags,
        template_slug=template.slug if template else None,
        limit=1,
    )
    return recs[0] if recs else None
