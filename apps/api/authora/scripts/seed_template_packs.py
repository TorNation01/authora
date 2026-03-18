"""Seed template packs from definitions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.data.template_pack_definitions import TEMPLATE_PACK_DEFINITIONS
from authora.models import TemplatePack


async def seed_template_packs() -> None:
    """Seed or update template packs from definitions."""
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        for defn in TEMPLATE_PACK_DEFINITIONS:
            result = await session.execute(select(TemplatePack).where(TemplatePack.slug == defn["slug"]))
            existing = result.scalar_one_or_none()

            data = {
                "name": defn["name"],
                "description": defn.get("description"),
                "price_cents": defn["price_cents"],
                "stripe_price_id": defn.get("stripe_price_id"),
                "template_slugs": defn.get("template_slugs", []),
                "sort_order": defn.get("sort_order", 0),
                "is_active": defn.get("is_active", True),
            }

            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                session.add(existing)
            else:
                t = TemplatePack(slug=defn["slug"], **data)
                session.add(t)

        await session.commit()
        print(f"Seeded {len(TEMPLATE_PACK_DEFINITIONS)} template packs.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_template_packs())
