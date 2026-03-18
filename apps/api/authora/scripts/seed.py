"""Seed database with demo data: users, project templates, writing frameworks."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.models import User
from authora.services.auth import hash_password


TEST_USERS = [
    ("admin@authora.local", "admin123", "Admin", True),
    ("test@authora.local", "test123", "Test User", False),
]


async def seed_users(session):
    """Seed test users."""
    created = []
    for email, password, display_name, is_admin in TEST_USERS:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            continue
        user = User(
            email=email,
            hashed_password=hash_password(password),
            display_name=display_name,
            is_admin=is_admin,
            is_active=True,
        )
        session.add(user)
        created.append(f"{email} / {password}")
    if created:
        await session.commit()
        for c in created:
            print(f"Created user: {c}")
    else:
        print("All test users already exist.")


async def seed():
    """Seed users, then project templates and writing frameworks."""
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_users(session)

    await engine.dispose()

    # Run template and framework seeds (they use their own sessions)
    from authora.scripts.seed_project_templates import seed_project_templates
    from authora.scripts.seed_writing_frameworks import seed_writing_frameworks

    await seed_project_templates()
    await seed_writing_frameworks()


if __name__ == "__main__":
    asyncio.run(seed())
