"""Pytest configuration and fixtures."""

import asyncio
import contextlib
import os
import uuid
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Set test env before any authora imports
_db_url = os.environ.get("DATABASE_URL", "postgresql://authora:authora@localhost:5432/authora_test")
if _db_url.rstrip("/").endswith("/authora") and "authora_test" not in _db_url:
    _db_url = _db_url.rsplit("/", 1)[0] + "/authora_test"
os.environ["DATABASE_URL"] = _db_url
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")  # Use DB 1 for tests
os.environ.setdefault("DEPLOYMENT_MODE", "standalone")
# The suite registers more than five users from one client IP, which is the
# production brute-force ceiling. Without this the sixth registration is a
# 429 and every test after it fails on a missing access_token.
os.environ.setdefault("RATE_LIMIT_AUTH_ATTEMPTS", "1000")
# The suite creates many accounts on @example.com; the per-domain signup
# throttle is exercised in its own test with a small limit.
os.environ.setdefault("SIGNUP_DOMAIN_LIMIT_PER_HOUR", "1000")

from authora.database import Base, async_session_factory, engine, get_db
from authora.main import app
from authora.models import User
from authora.services.auth import create_access_token, create_user, hash_password




API_DIR = Path(__file__).resolve().parents[1]


def _database_name() -> str:
    return os.environ["DATABASE_URL"].rsplit("/", 1)[-1].split("?")[0]


async def _reset_schema_and_migrate() -> None:
    """Drop the test schema, then rebuild it from the Alembic chain.

    Destructive, so it refuses any database whose name does not end in _test: a
    misconfigured DATABASE_URL must stop the run, never wipe a real database.
    """
    name = _database_name()
    if not name.endswith("_test"):
        raise RuntimeError(
            f"refusing to reset schema of {name!r}: tests only rebuild *_test databases"
        )

    # Drop tables and enum types, never the schema: dropping `public` also drops
    # the pgvector extension, and the application role is not allowed to create
    # it again (migration 021 assumes it pre-exists).
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                DO $$
                DECLARE r record;
                BEGIN
                    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
                    LOOP
                        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                    FOR r IN
                        SELECT t.typname FROM pg_type t
                        JOIN pg_namespace n ON n.oid = t.typnamespace
                        WHERE n.nspname = 'public' AND t.typtype = 'e'
                    LOOP
                        EXECUTE 'DROP TYPE IF EXISTS public.' || quote_ident(r.typname) || ' CASCADE';
                    END LOOP;
                END $$;
                """
            )
        )

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(API_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    await asyncio.to_thread(command.upgrade, cfg, "head")


@pytest.fixture(scope="session")
async def init_test_db():
    """Build the test database from migrations. Run once per session.

    ``Base.metadata.create_all`` used to build this schema, which skipped the
    migration chain entirely: rows that migrations seed (the five billing plans
    from 016, the trial columns from 071) never existed, so
    test_list_plans_public asserted against an empty plans table, and nothing
    ever cleaned state between runs, so a second run collided on
    users_email and took 53 tests down with it. Rebuilding from
    ``alembic upgrade head`` starts every run from the schema a fresh deploy
    would produce, and fails the suite if a migration stops applying.
    """
    try:
        await _reset_schema_and_migrate()
    except RuntimeError:
        raise
    except Exception as e:
        pytest.skip(f"Database unavailable: {e}")
    yield
    await engine.dispose()


@pytest.fixture
async def db_conn(init_test_db):
    """One connection carrying the test's transaction, always rolled back."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            yield conn
        finally:
            await trans.rollback()


@contextlib.asynccontextmanager
async def _request_session(conn):
    """A session scoped to one request, bound to the test's transaction.

    Production hands every request a new AsyncSession, so each request starts
    with an empty identity map. Sharing one session across requests made a
    chapter that a request had deleted still visible through the relationship
    the previous request had loaded - a shape that cannot happen in production
    and that hid whether deletion actually worked. Commits become savepoints, so
    nothing outlives the test.
    """
    session = AsyncSession(
        bind=conn,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@pytest.fixture
async def db(db_conn):
    """Session for the test body to set up and inspect rows directly."""
    async with _request_session(db_conn) as session:
        yield session


@pytest.fixture
async def client(db_conn):
    """Async HTTP client with DB override for integration tests."""
    async def override_get_db():
        async with _request_session(db_conn) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def anon_client():
    """Client without auth - for public endpoints (health, setup, etc.)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a regular test user."""
    user = User(
        email=f"user-{uuid.uuid4().hex[:10]}@example.com",
        hashed_password=hash_password("testpass123"),
        display_name="Test User",
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
async def admin_user(db: AsyncSession):
    """Create an admin test user."""
    user = User(
        email=f"admin-{uuid.uuid4().hex[:10]}@example.com",
        hashed_password=hash_password("adminpass123"),
        display_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
def token(test_user):
    """Bearer token for regular user."""
    access_token, _ = create_access_token(test_user.id)
    return access_token


@pytest.fixture
def admin_token(admin_user):
    """Bearer token for admin user."""
    access_token, _ = create_access_token(admin_user.id)
    return access_token


@contextlib.asynccontextmanager
async def _authorised_client(db_conn, token: str):
    """A client of its own, carrying one token.

    Separate clients rather than one shared client with a header swapped: a test
    that asks for both a regular and an admin caller must be able to make a
    request as each, and header mutation on a shared object silently made both
    requests admin.
    """
    async def override_get_db():
        async with _request_session(db_conn) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(db_conn, token):
    """Client with regular user auth headers."""
    async with _authorised_client(db_conn, token) as ac:
        yield ac


@pytest.fixture
async def admin_client(db_conn, admin_token):
    """Client with admin auth headers."""
    async with _authorised_client(db_conn, admin_token) as ac:
        yield ac
