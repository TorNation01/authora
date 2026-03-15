"""Pytest configuration and fixtures."""

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Set test env before any authora imports
_db_url = os.environ.get("DATABASE_URL", "postgresql://authora:authora@localhost:5432/authora_test")
if _db_url.rstrip("/").endswith("/authora") and "authora_test" not in _db_url:
    _db_url = _db_url.rsplit("/", 1)[0] + "/authora_test"
os.environ["DATABASE_URL"] = _db_url
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")  # Use DB 1 for tests
os.environ.setdefault("DEPLOYMENT_MODE", "standalone")

from authora.database import Base, async_session_factory, engine, get_db
from authora.main import app
from authora.models import User
from authora.services.auth import create_access_token, create_user, hash_password




@pytest.fixture(scope="session")
async def init_test_db():
    """Create test database tables. Run once per session. Skips if DB unavailable."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        pytest.skip(f"Database unavailable: {e}")
    yield
    await engine.dispose()


@pytest.fixture
async def db(init_test_db):
    """Provide a database session for each test. Rolls back after test."""
    async with async_session_factory() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def client(db: AsyncSession):
    """Async HTTP client with DB override for integration tests."""
    async def override_get_db():
        yield db

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
        email="test@example.com",
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
        email="admin@example.com",
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


@pytest.fixture
async def auth_client(client, token):
    """Client with regular user auth headers."""
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def admin_client(client, admin_token):
    """Client with admin auth headers."""
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client
