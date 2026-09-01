"""Seed Authora v2 database — real plans, pricing, and founder account."""
import asyncio, sys, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from authora.config import get_settings
from authora.models import Plan, User, Subscription
from authora.data.template_definitions import TEMPLATE_DEFINITIONS
from authora.models import ProjectTemplate

# ── v2 Plans ──────────────────────────────────────────────────
V2_PLANS = [
    {
        "slug": "free",
        "name": "Free",
        "sort_order": 0,
        "price_monthly_cents": 0,
        "price_yearly_cents": 0,
        "limits": {
            "books": 3,
            "projects": 1,
            "ai_actions_per_month": 20,
            "exports_per_month": 5,
            "export_formats": ["docx", "txt"],
            "ghostwriter_sessions_per_month": 0,
            "storage_mb": 100,
        },
        "features": [
            "templates_free",
            "basic_export",
            "ai_assist_basic",
            "accountability",
        ],
    },
    {
        "slug": "starter",
        "name": "Starter",
        "sort_order": 1,
        "price_monthly_cents": 1200,
        "price_yearly_cents": 9900,
        "limits": {
            "books": 5,
            "projects": 3,
            "ai_actions_per_month": 100,
            "exports_per_month": 20,
            "export_formats": ["docx", "txt", "pdf"],
            "ghostwriter_sessions_per_month": 0,
            "storage_mb": 500,
        },
        "features": [
            "templates_free",
            "basic_export",
            "ai_assist_enhanced",
            "accountability",
            "pdf_export",
        ],
    },
    {
        "slug": "pro",
        "name": "Pro",
        "sort_order": 2,
        "price_monthly_cents": 2900,
        "price_yearly_cents": 24900,
        "limits": {
            "books": -1,  # unlimited
            "projects": -1,
            "ai_actions_per_month": 500,
            "exports_per_month": 50,
            "export_formats": ["docx", "txt", "pdf", "epub"],
            "ghostwriter_sessions_per_month": 30,
            "storage_mb": 2000,
        },
        "features": [
            "templates_all",
            "all_exports",
            "ai_assist_full",
            "ghostwriter",
            "accountability",
            "revision_assistant",
            "research_assistant",
            "chapter_workflow",
        ],
    },
    {
        "slug": "studio",
        "name": "Studio",
        "sort_order": 3,
        "price_monthly_cents": 7900,
        "price_yearly_cents": 69900,
        "limits": {
            "books": -1,
            "projects": -1,
            "ai_actions_per_month": -1,  # unlimited
            "exports_per_month": -1,
            "export_formats": ["docx", "txt", "pdf", "epub", "html"],
            "ghostwriter_sessions_per_month": -1,
            "storage_mb": 10000,
        },
        "features": [
            "templates_all",
            "all_exports",
            "ai_assist_unlimited",
            "ghostwriter",
            "accountability",
            "revision_assistant",
            "research_assistant",
            "chapter_workflow",
            "team_collaboration",
            "priority_support",
            "custom_branding",
        ],
    },
    {
        "slug": "founder_lifetime",
        "name": "Founder Lifetime",
        "sort_order": 4,
        "price_lifetime_cents": 49900,
        "limits": {
            "books": -1,
            "projects": -1,
            "ai_actions_per_month": -1,
            "exports_per_month": -1,
            "export_formats": ["docx", "txt", "pdf", "epub", "html"],
            "ghostwriter_sessions_per_month": -1,
            "storage_mb": -1,
        },
        "features": [
            "templates_all",
            "all_exports",
            "ai_assist_unlimited",
            "ghostwriter",
            "accountability",
            "revision_assistant",
            "research_assistant",
            "chapter_workflow",
            "team_collaboration",
            "priority_support",
            "custom_branding",
            "founder_badge",
            "early_access",
            "lifetime_access",
        ],
    },
]

FOUNDER_EMAIL = "70rn4710n@proton.me"
FOUNDER_PASSWORD = "AuthoraTest1"


async def seed_v2() -> None:
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # ── Plans ──────────────────────────────────────────
        for pdef in V2_PLANS:
            r = await session.execute(select(Plan).where(Plan.slug == pdef["slug"]))
            existing = r.scalar_one_or_none()
            if existing:
                for k, v in pdef.items():
                    setattr(existing, k, v)
                session.add(existing)
            else:
                session.add(Plan(id=uuid.uuid4(), **pdef))
        await session.commit()
        print(f"Seeded {len(V2_PLANS)} plans.")

        # ── Founder account ────────────────────────────────
        from authora.services.auth import hash_password

        r = await session.execute(select(User).where(User.email == FOUNDER_EMAIL))
        user = r.scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=FOUNDER_EMAIL,
                hashed_password=hash_password(FOUNDER_PASSWORD),
                is_active=True,
                is_admin=True,
                billing_exempt=True,
            )
            session.add(user)
            await session.flush()
            print(f"Created founder user: {FOUNDER_EMAIL}")
        else:
            user.hashed_password = hash_password(FOUNDER_PASSWORD)
            user.is_admin = True
            user.billing_exempt = True
            user.is_active = True
            session.add(user)
            await session.flush()
            print(f"Updated founder user: {FOUNDER_EMAIL}")

        # ── Founder lifetime subscription ──────────────────
        founder_plan = (await session.execute(
            select(Plan).where(Plan.slug == "founder_lifetime")
        )).scalar_one()

        r = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.is_lifetime == True,
            )
        )
        sub = r.scalar_one_or_none()
        if not sub:
            sub = Subscription(
                id=uuid.uuid4(),
                user_id=user.id,
                plan_id=founder_plan.id,
                status="active",
                is_lifetime=True,
            )
            session.add(sub)
            print("Created founder lifetime subscription.")
        else:
            sub.plan_id = founder_plan.id
            sub.status = "active"
            session.add(sub)
            print("Updated founder lifetime subscription.")

        await session.commit()

        # ── Templates ──────────────────────────────────────
        slug_to_id: dict[str, str] = {}
        for defn in TEMPLATE_DEFINITIONS:
            slug = defn["slug"]
            parent_slug = defn.get("parent_slug")
            parent_id = uuid.UUID(slug_to_id[parent_slug]) if parent_slug and parent_slug in slug_to_id else None

            r = await session.execute(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
            existing = r.scalar_one_or_none()

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
        print(f"Seeded {len(TEMPLATE_DEFINITIONS)} templates.")

    await engine.dispose()
    print("\n✓ Authora v2 database seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_v2())
