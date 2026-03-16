"""Authentication service."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Session, User


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Create JWT access token."""
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires, "type": "access"}
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, expires


def create_refresh_token() -> tuple[str, str, datetime]:
    """Create refresh token and its hash for storage."""
    settings = get_settings()
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return token, token_hash, expires


def decode_token(token: str) -> dict | None:
    """Decode and validate JWT token."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, display_name: str | None = None) -> User:
    """Create new user."""
    user = User(
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def create_session(db: AsyncSession, user_id: uuid.UUID) -> tuple[str, str, datetime]:
    """Create session and return refresh token."""
    token, token_hash, expires = create_refresh_token()
    session = Session(user_id=user_id, token_hash=token_hash, expires_at=expires)
    db.add(session)
    await db.flush()
    return token, token_hash, expires


async def get_session_by_token_hash(db: AsyncSession, token_hash: str) -> Session | None:
    """Get valid session by token hash."""
    result = await db.execute(
        select(Session).where(Session.token_hash == token_hash, Session.expires_at > datetime.now(timezone.utc))
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, token_hash: str) -> None:
    """Delete session (logout)."""
    result = await db.execute(select(Session).where(Session.token_hash == token_hash))
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, *, display_name: str | None = None
) -> User | None:
    """Update user profile. Returns updated user or None."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    user.display_name = (display_name.strip() if display_name else None) or None
    await db.flush()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession, user_id: uuid.UUID, current_password: str, new_password: str
) -> bool:
    """Change user password. Returns True if successful."""
    user = await get_user_by_id(db, user_id)
    if not user or not verify_password(current_password, user.hashed_password):
        return False
    user.hashed_password = hash_password(new_password)
    await db.flush()
    return True
