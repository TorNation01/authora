"""Seed writing frameworks from framework_definitions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.data.framework_definitions import FRAMEWORK_DEFINITIONS
from authora.models import WritingFramework


async def seed_writing_frameworks() -> None:
    """Seed or update writing frameworks from definitions."""
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        for defn in FRAMEWORK_DEFINITIONS:
            slug = defn["slug"]
            result = await session.execute(select(WritingFramework).where(WritingFramework.slug == slug))
            existing = result.scalar_one_or_none()

            data = {
                "book_type": defn["book_type"],
                "name": defn["name"],
                "description": defn.get("description"),
                "ideal_use_cases": defn.get("ideal_use_cases"),
                "ideal_genres": defn.get("ideal_genres"),
                "planning_stages": defn.get("planning_stages"),
                "beat_stages": defn.get("beat_stages"),
                "chapter_structure": defn.get("chapter_structure"),
                "manuscript_scaffolding": defn.get("manuscript_scaffolding"),
                "chapter_skeletons": defn.get("chapter_skeletons"),
                "milestone_logic": defn.get("milestone_logic"),
                "accountability_mapping": defn.get("accountability_mapping"),
                "revision_checklist": defn.get("revision_checklist"),
                "ai_prompt_presets": defn.get("ai_prompt_presets"),
                "recommendation_rules": defn.get("recommendation_rules"),
                "scene_prompts": defn.get("scene_prompts"),
                "sort_order": defn.get("sort_order", 0),
                "is_featured": defn.get("is_featured", False),
                "is_disabled": defn.get("is_disabled", False),
            }

            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                session.add(existing)
            else:
                wf = WritingFramework(slug=slug, **data)
                session.add(wf)

        await session.commit()
        print(f"Seeded {len(FRAMEWORK_DEFINITIONS)} writing frameworks.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_writing_frameworks())
