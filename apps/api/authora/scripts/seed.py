"""Seed database with demo data."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.models import User
from authora.services.auth import hash_password


async def seed():
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User))
        if result.scalars().first():
            print("Users exist, skipping seed.")
            return

        admin = User(
            email="admin@authora.local",
            hashed_password=hash_password("admin123"),
            display_name="Admin",
            is_admin=True,
        )
        session.add(admin)
        await session.commit()
        print("Created admin user: admin@authora.local / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
