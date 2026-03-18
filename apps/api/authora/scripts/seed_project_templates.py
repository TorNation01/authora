"""Seed project templates from template_definitions into the database."""

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.data.template_definitions import TEMPLATE_DEFINITIONS
from authora.models import ProjectTemplate


async def seed_project_templates() -> None:
    """Seed or update project templates from definitions."""
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    slug_to_id: dict[str, str] = {}

    async with async_session() as session:
        # First pass: create/update all templates, collect slug->id
        for defn in TEMPLATE_DEFINITIONS:
            slug = defn["slug"]
            parent_slug = defn.get("parent_slug")
            parent_id = uuid.UUID(slug_to_id[parent_slug]) if parent_slug and parent_slug in slug_to_id else None

            result = await session.execute(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
            existing = result.scalar_one_or_none()

            data = {
                "category": defn["category"],
                "name": defn["name"],
                "access_level": defn.get("access_level", "free"),
                "premium_pack_slug": defn.get("premium_pack_slug"),
                "description": defn.get("description"),
                "who_it_is_for": defn.get("who_it_is_for"),
                "expected_outcome": defn.get("expected_outcome"),
                "suggested_workflow": defn.get("suggested_workflow"),
                "book_type": defn.get("book_type"),
                "genre": defn.get("genre"),
                "structure_framework": defn.get("structure_framework"),
                "default_structure": defn.get("default_structure"),
                "default_milestones": defn.get("default_milestones"),
                "default_planning_prompts": defn.get("default_planning_prompts"),
                "default_accountability": defn.get("default_accountability"),
                "ai_prompts": defn.get("ai_prompts"),
                "export_recommendations": defn.get("export_recommendations"),
                "setup_questions": defn.get("setup_questions"),
                "chapter_skeletons": defn.get("chapter_skeletons"),
                "sort_order": defn.get("sort_order", 0),
                "is_featured": defn.get("is_featured", False),
                "is_disabled": defn.get("is_disabled", False),
            }

            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                existing.parent_id = parent_id
                session.add(existing)
                slug_to_id[slug] = str(existing.id)
            else:
                t = ProjectTemplate(slug=slug, parent_id=parent_id, **data)
                session.add(t)
                await session.flush()
                slug_to_id[slug] = str(t.id)

        await session.commit()
        print(f"Seeded {len(TEMPLATE_DEFINITIONS)} project templates.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_project_templates())
