"""Auth API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.models import UserPreference
from authora.database import get_db
from authora.schemas.auth import (
    LogoutRequest,
    PasswordChange,
    RefreshRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from authora.core.audit import AuditLogger
from authora.services.auth import (
    change_password,
    create_access_token,
    create_session,
    create_user,
    delete_session,
    get_session_by_token_hash,
    get_user_by_email,
    get_user_by_id,
    update_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register new user. Standalone mode only."""
    if not get_settings().feature_standalone_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration is disabled in this deployment",
        )
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await create_user(db, data.email, data.password, data.display_name)
    refresh_token, _, _ = await create_session(db, user.id)
    access_token, expires = create_access_token(user.id)

    audit = AuditLogger(db)
    await audit.log("register", "user", str(user.id), user.id, {"email": data.email})

    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((expires.timestamp() - __import__("datetime").datetime.now(__import__("datetime").timezone.utc).timestamp())),
    )


@router.post("/login", response_model=Token)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get tokens. Disabled when using SSO-only auth."""
    if not get_settings().feature_standalone_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local login is disabled. Use SSO.",
        )
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    refresh_token, _, _ = await create_session(db, user.id)
    access_token, expires = create_access_token(user.id)

    audit = AuditLogger(db)
    await audit.log("login", "user", str(user.id), user.id)

    await db.commit()

    from datetime import datetime, timezone
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(expires.timestamp() - datetime.now(timezone.utc).timestamp()),
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    import hashlib

    refresh_token = body.refresh_token
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    session = await get_session_by_token_hash(db, token_hash)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token, expires = create_access_token(session.user_id)
    from datetime import datetime, timezone
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(expires.timestamp() - datetime.now(timezone.utc).timestamp()),
    )


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """Logout and invalidate refresh token."""
    import hashlib

    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    await delete_session(db, token_hash)
    await db.commit()
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    """Get current user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        created_at=current_user.created_at,
        is_admin=current_user.is_admin,
    )


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""

    if not get_settings().feature_standalone_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile updates are disabled in this deployment",
        )

    updates = data.model_dump(exclude_unset=True)
    if "display_name" not in updates:
        user = await get_user_by_id(db, current_user.id)
    else:
        user = await update_user(db, current_user.id, display_name=updates["display_name"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.commit()
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
        is_admin=user.is_admin,
    )


@router.patch("/me/password")
async def change_my_password(
    data: PasswordChange,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Change current user password."""

    if not get_settings().feature_standalone_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password change is disabled in this deployment",
        )

    ok = await change_password(
        db,
        current_user.id,
        data.current_password,
        data.new_password,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    await db.commit()
    return {"message": "Password updated"}


class PreferencesResponse(BaseModel):
    preferences: dict


class PreferencesUpdate(BaseModel):
    preferences: dict


@router.get("/me/preferences", response_model=PreferencesResponse)
async def get_my_preferences(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get current user preferences (JSONB key-value)."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    return PreferencesResponse(preferences=pref.preferences if pref else {})


@router.patch("/me/preferences", response_model=PreferencesResponse)
async def update_my_preferences(
    data: PreferencesUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update current user preferences. Merges with existing."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id, preferences=data.preferences)
        db.add(pref)
    else:
        merged = {**(pref.preferences or {}), **data.preferences}
        pref.preferences = merged
    await db.commit()
    await db.refresh(pref)
    return PreferencesResponse(preferences=pref.preferences or {})


# --- AI Personalization ---

from datetime import datetime, timezone
from authora.schemas.ai_personalization import (
    AIPersonalizationLearnRequest,
    AIPersonalizationResponse,
    AIPersonalizationUpdate,
    StyleProfile,
)

AI_PERSONALIZATION_KEY = "ai_personalization"
DEFAULT_PERSONALIZATION = {"enabled": False, "tone_preferences": [], "style_profile": None, "updated_at": None}


def _get_personalization(pref: UserPreference | None) -> dict:
    if not pref or not pref.preferences:
        return dict(DEFAULT_PERSONALIZATION)
    p = pref.preferences.get(AI_PERSONALIZATION_KEY)
    if not p or not isinstance(p, dict):
        return dict(DEFAULT_PERSONALIZATION)
    return {**DEFAULT_PERSONALIZATION, **p}


def _to_response(p: dict) -> AIPersonalizationResponse:
    sp = p.get("style_profile")
    return AIPersonalizationResponse(
        enabled=p.get("enabled", False),
        tone_preferences=p.get("tone_preferences") or [],
        style_profile=StyleProfile(**sp) if isinstance(sp, dict) else None,
        updated_at=p.get("updated_at"),
    )


@router.get("/me/ai-personalization", response_model=AIPersonalizationResponse)
async def get_ai_personalization(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get AI personalization settings. Optional: adapts AI to your writing style."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    p = _get_personalization(pref)
    return _to_response(p)


@router.patch("/me/ai-personalization", response_model=AIPersonalizationResponse)
async def update_ai_personalization(
    data: AIPersonalizationUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update AI personalization. Turn on/off, set tone preferences, or update style profile."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id, preferences={})
        db.add(pref)
    p = _get_personalization(pref)
    updates = data.model_dump(exclude_unset=True)
    if "enabled" in updates:
        p["enabled"] = updates["enabled"]
    if "tone_preferences" in updates:
        p["tone_preferences"] = updates["tone_preferences"] or []
    if "style_profile" in updates:
        sp = updates["style_profile"]
        p["style_profile"] = sp.model_dump() if sp else None
    p["updated_at"] = datetime.now(timezone.utc).isoformat()
    merged = pref.preferences or {}
    merged[AI_PERSONALIZATION_KEY] = p
    pref.preferences = merged
    await db.commit()
    await db.refresh(pref)
    return _to_response(p)


@router.post("/me/ai-personalization/learn", response_model=AIPersonalizationResponse)
async def learn_ai_personalization(
    data: AIPersonalizationLearnRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Learn style from a book's content. Derives tone and sentence structure."""
    from authora.models import Book, Chapter, Project
    from authora.services.export import tiptap_to_plain_text
    from authora.services.ai_personalization import derive_style_from_content

    try:
        book_id = uuid.UUID(data.book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book_id")

    result = await db.execute(
        select(Book).join(Project).where(Book.id == book_id, Project.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    ch_result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order).limit(10)
    )
    chapters = ch_result.scalars().all()
    text_parts = []
    for ch in chapters:
        if ch.content:
            text_parts.append(tiptap_to_plain_text(ch.content))
    combined = "\n\n".join(text_parts)

    derived = derive_style_from_content(combined)
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id, preferences={})
        db.add(pref)
    p = _get_personalization(pref)
    p["style_profile"] = derived
    p["enabled"] = True  # Turn on when learning
    p["updated_at"] = datetime.now(timezone.utc).isoformat()
    merged = pref.preferences or {}
    merged[AI_PERSONALIZATION_KEY] = p
    pref.preferences = merged
    await db.commit()
    await db.refresh(pref)
    return _to_response(p)


@router.post("/me/ai-personalization/reset", response_model=AIPersonalizationResponse)
async def reset_ai_personalization(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reset style profile. Keeps enabled/tone_preferences; clears learned style."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        return _to_response(dict(DEFAULT_PERSONALIZATION))
    p = _get_personalization(pref)
    p["style_profile"] = None
    p["updated_at"] = datetime.now(timezone.utc).isoformat()
    merged = pref.preferences or {}
    merged[AI_PERSONALIZATION_KEY] = p
    pref.preferences = merged
    await db.commit()
    await db.refresh(pref)
    return _to_response(p)
