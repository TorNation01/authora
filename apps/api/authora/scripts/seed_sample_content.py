"""Seed sample projects, books, and chapters for testing the system in action."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.models import Book, Chapter, Project, User

# TipTap doc format for chapter content
SAMPLE_CHAPTER_CONTENT = {
    "type": "doc",
    "content": [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "The rain had been falling for three days when Elena first saw the stranger at the edge of the woods. She had been watching from the kitchen window, absently stirring her tea, when a figure emerged from the treeline—tall, hooded, moving with purpose toward the old mill."
                }
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Something about the way they walked made her set down her cup. The village had been quiet since the disappearances began. Too quiet."
                }
            ]
        }
    ]
}

SAMPLE_CHAPTER_2 = {
    "type": "doc",
    "content": [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Marcus had always believed that the best ideas came at 3 a.m. His editor disagreed. The manuscript was due in six weeks, and he had written exactly forty-seven words. Forty-seven words that he had already deleted twice."
                }
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "He stared at the blank screen. The cursor blinked. Somewhere in the city, a siren wailed. He took a sip of cold coffee and began to type."
                }
            ]
        }
    ]
}

SAMPLE_CHAPTER_3 = {
    "type": "doc",
    "content": [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "The workshop had been in her family for four generations. Sawdust still clung to the rafters from her grandfather's last project—a rocking chair that had never been finished. She ran her hand along the workbench, feeling the grooves and scars of decades of use."
                }
            ]
        }
    ]
}


async def seed_sample_content(session):
    """Create sample projects, books, and chapters for admin@authora.local."""
    result = await session.execute(select(User).where(User.email == "admin@authora.local"))
    admin = result.scalar_one_or_none()
    if not admin:
        print("Admin user (admin@authora.local) not found. Run npm run db:seed first.")
        return

    # Check if sample content already exists
    existing = await session.execute(
        select(Project).where(Project.user_id == admin.id, Project.name == "Sample Novel: The Mill")
    )
    if existing.scalar_one_or_none():
        print("Sample content already exists. Skipping.")
        return

    # Project 1: Fiction novel
    p1 = Project(
        user_id=admin.id,
        name="Sample Novel: The Mill",
        guidance_mode="guided",
        knowledge_mode="fiction",
    )
    session.add(p1)
    await session.flush()

    b1 = Book(
        project_id=p1.id,
        title="The Mill at Winter's Edge",
        type="fiction",
        genre="Mystery",
    )
    session.add(b1)
    await session.flush()

    ch1 = Chapter(
        book_id=b1.id,
        title="Chapter 1: The Stranger",
        sort_order=0,
        content=SAMPLE_CHAPTER_CONTENT,
        word_count=87,
        section_status="draft",
    )
    session.add(ch1)
    await session.flush()

    ch2 = Chapter(
        book_id=b1.id,
        title="Chapter 2: The Investigation",
        sort_order=1,
        content=SAMPLE_CHAPTER_2,
        word_count=92,
        section_status="draft",
    )
    session.add(ch2)

    ch3 = Chapter(
        book_id=b1.id,
        title="Chapter 3: The Workshop",
        sort_order=2,
        content=SAMPLE_CHAPTER_3,
        word_count=58,
        section_status="done",
    )
    session.add(ch3)

    # Project 2: Memoir
    p2 = Project(
        user_id=admin.id,
        name="Sample Memoir: Notes from the Road",
        guidance_mode="flexible",
        knowledge_mode="memoir",
    )
    session.add(p2)
    await session.flush()

    b2 = Book(
        project_id=p2.id,
        title="Notes from the Road",
        type="nonfiction",
        genre="Memoir",
    )
    session.add(b2)
    await session.flush()

    memoir_content = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "I left on a Tuesday. The car was packed with everything I thought I needed: a tent, a sleeping bag, three changes of clothes, and a notebook. The notebook was the only thing I never regretted bringing."
                    }
                ]
            }
        ]
    }

    ch4 = Chapter(
        book_id=b2.id,
        title="Prologue: Tuesday",
        sort_order=0,
        content=memoir_content,
        word_count=52,
        section_status="draft",
    )
    session.add(ch4)

    await session.commit()
    print("Seeded sample content:")
    print("  - Project: Sample Novel: The Mill (3 chapters)")
    print("  - Project: Sample Memoir: Notes from the Road (1 chapter)")
    print("  - Login as admin@authora.local / admin123 to view")


async def main():
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_sample_content(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
