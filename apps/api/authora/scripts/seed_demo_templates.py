"""Seed demo templates for fiction and nonfiction books."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.models import Setting
from authora.scripts.demo_templates_data import FICTION_TEMPLATE, NONFICTION_TEMPLATE


async def seed_demo_templates():
    """Seed fiction and nonfiction demo templates into settings."""
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        r = await session.execute(select(Setting).where(Setting.key == "demo_templates_seeded"))
        if r.scalar_one_or_none():
            print("Demo templates already seeded.")
            await engine.dispose()
            return

        templates = [
            Setting(key="template_fiction_demo", value=FICTION_TEMPLATE),
            Setting(key="template_nonfiction_demo", value=NONFICTION_TEMPLATE),
            Setting(key="demo_templates_seeded", value={"seeded": True}),
        ]
        for t in templates:
            session.merge(t)
        await session.commit()
        print("Seeded fiction and nonfiction demo templates.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_demo_templates())
