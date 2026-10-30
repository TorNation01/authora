"""Auth API routes."""

import uuid
import secrets
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select

from authora.models import User
from authora.models.analytics_event import AnalyticsEvent
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
from authora.services.turnstile import (
    TurnstileUnavailable,
    site_key_for_browser,
    verify_turnstile_token,
)
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


def _signup_invite_codes(settings) -> list[str]:
    return [c.strip() for c in (settings.signup_invite_codes or "").split(",") if c.strip()]


def _request_ip(request: Request) -> str | None:
    """Client IP for Cloudflare, preferring the header the tunnel sets."""
    for header in ("cf-connecting-ip", "x-forwarded-for"):
        value = request.headers.get(header)
        if value:
            return value.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("/signup-config")
async def signup_config() -> dict:
    """What the register page must render, decided by the server.

    Declared ahead of the parameterised routes so the literal path is not
    swallowed by a `/{...}` match, and public because the page needs it before
    the visitor has an account.
    """
    settings = get_settings()
    return {
        "invite_required": bool(_signup_invite_codes(settings)),
        "turnstile": {
            "enabled": bool(settings.turnstile_secret_key and settings.turnstile_site_key),
            "site_key": site_key_for_browser(
                settings.turnstile_secret_key, settings.turnstile_site_key
            ),
        },
        "standalone_auth": settings.feature_standalone_auth,
    }


@router.post("/register", response_model=Token)
async def register(
    data: UserCreate,
    request: Request,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Register new user. Standalone mode only."""
    settings = get_settings()
    if not settings.feature_standalone_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration is disabled in this deployment",
        )

    # Invite-only gate: when codes are configured, no account exists without one.
    invite_codes = _signup_invite_codes(settings)
    if invite_codes:
        supplied = (data.invite_code or "").strip()
        if not supplied or not any(secrets.compare_digest(supplied, code) for code in invite_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authora is invite-only. A valid invite code is required.",
            )

    # Bot protection: when Turnstile is configured it guards every registration,
    # so lifting the beta gate (empty invite codes) cannot silently open signup to
    # scripts. Checked before the email lookup so probing costs a challenge.
    if settings.turnstile_secret_key:
        token = (data.turnstile_token or "").strip()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bot verification required. Please complete the challenge and try again.",
            )
        try:
            passed = await verify_turnstile_token(
                token,
                settings.turnstile_secret_key,
                remote_ip=_request_ip(request),
                verify_url=settings.turnstile_verify_url,
            )
        except TurnstileUnavailable:
            # Fail closed, but say so: a Cloudflare blip must not read as a bad code.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Bot verification is temporarily unavailable. Please retry in a moment.",
            )
        if not passed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bot verification failed. Please complete the challenge again.",
            )

    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await create_user(db, data.email, data.password, data.display_name)

    # Signup funnel: a new account starts on a trial (Starter by default), so
    # the first chapter is written with real entitlements instead of Free-plan
    # walls. Stamped before the commit so the very first /billing/status read
    # already reports the trial.
    trial_started = False
    if getattr(settings, "feature_billing", False):
        from authora.services.billing_service import start_signup_trial

        trial_started = start_signup_trial(
            user,
            int(getattr(settings, "signup_trial_days", 0) or 0),
            str(getattr(settings, "signup_trial_plan", "") or ""),
        )
        if trial_started:
            db.add(
                AnalyticsEvent(
                    user_id=user.id,
                    event_type="trial_started",
                    resource_type="user",
                    resource_id=str(user.id),
                    properties={
                        "plan_slug": user.trial_plan_slug,
                        "days": int(getattr(settings, "signup_trial_days", 0) or 0),
                        "ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None,
                        "invite_gated": bool([c for c in (settings.signup_invite_codes or "").split(",") if c.strip()]),
                    },
                )
            )
    refresh_token, _, _ = await create_session(db, user.id)
    access_token, expires = create_access_token(user.id)

    audit = AuditLogger(db)
    await audit.log("register", "user", str(user.id), user.id, {"email": data.email})

    if data.referral_code:
        from authora.services.growth_service import resolve_referral_on_signup
        from authora.services.network_effect_service import (
            is_creator,
            record_creator_signup_attributed,
        )

        ref = await resolve_referral_on_signup(db, user.id, data.referral_code)
        inviter_id = ref.inviter_id if ref else None
        if not inviter_id:
            inviter = await db.execute(
                select(User).where(User.referral_code == data.referral_code).limit(1)
            )
            u = inviter.scalar_one_or_none()
            inviter_id = u.id if u else None
        if inviter_id and await is_creator(db, inviter_id):
            await record_creator_signup_attributed(
                db,
                inviter_id,
                user.id,
                referral_id=ref.id if ref else None,
                source="referral",
            )

    if data.affiliate_code and get_settings().feature_affiliate:
        from authora.services.affiliate_service import attribute_signup
        await attribute_signup(db, user.id, data.affiliate_code)

    await db.commit()

    # The welcome email carries the whole start-to-finish path, so a new
    # customer is never left guessing what to do first. It is queued after the
    # commit so a mail failure cannot roll back the account.
    from authora.services.transactional_email import send_welcome

    background.add_task(send_welcome, user.email, user.display_name)

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


class PushTokenRequest(BaseModel):
    """Register push notification token for mobile."""

    token: str
    platform: str  # ios | android


@router.post("/me/push-token")
async def register_push_token(
    data: PushTokenRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Register Expo push token for reminders, streaks, milestones. Replaces previous tokens for this platform."""
    if data.platform not in ("ios", "android"):
        raise HTTPException(status_code=400, detail="platform must be ios or android")
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id, preferences={})
        db.add(pref)
    tokens = (pref.preferences or {}).get("push_tokens") or []
    tokens = [t for t in tokens if isinstance(t, dict) and t.get("platform") != data.platform]
    tokens.append({"token": data.token, "platform": data.platform})
    pref.preferences = {**(pref.preferences or {}), "push_tokens": tokens}
    await db.commit()
    return {"ok": True}


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


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------
class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


def _reset_fingerprint(hashed_password: str) -> str:
    """Short digest of the current hash.

    Putting it in the token makes the link single-use without a token table:
    once the password changes, the embedded fingerprint no longer matches.
    """
    import hashlib

    return hashlib.sha256((hashed_password or "").encode()).hexdigest()[:16]


def _make_reset_token(user: User) -> str:
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    settings = get_settings()
    payload = {
        "sub": str(user.id),
        "purpose": "password_reset",
        "pwf": _reset_fingerprint(user.hashed_password),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Start a password reset.

    Always answers the same way, whether or not the address has an account —
    otherwise this endpoint becomes a way to test which emails are registered.
    """
    email = (data.email or "").strip().lower()
    if email:
        user = await get_user_by_email(db, email)
        if user and user.is_active:
            from authora.services.transactional_email import send_password_reset

            token = _make_reset_token(user)
            reset_url = f"{get_settings().app_base_url.rstrip('/')}/reset-password?token={token}"
            background.add_task(send_password_reset, user.email, reset_url, user.display_name)

    return {
        "message": "If that address has an account, a reset link is on its way. The link works for one hour.",
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Finish a password reset. One use only, one hour to use it."""
    from jose import JWTError, jwt
    from sqlalchemy import delete

    from authora.models import Session as SessionModel
    from authora.services.auth import hash_password

    if len(data.new_password or "") < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose a password of at least 8 characters.",
        )

    settings = get_settings()
    try:
        payload = jwt.decode(data.token or "", settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That reset link is not valid. Request a new one.",
        ) from None

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That reset link is not valid.")

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That reset link is not valid.") from None

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="That reset link is not valid.")

    if payload.get("pwf") != _reset_fingerprint(user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That reset link has already been used. Request a new one.",
        )

    user.hashed_password = hash_password(data.new_password)
    # A reset is a security event: every existing session is revoked.
    await db.execute(delete(SessionModel).where(SessionModel.user_id == user.id))
    await db.commit()

    audit = AuditLogger(db)
    await audit.log("password_reset", "user", str(user.id), user.id, {"via": "email_link"})
    await db.commit()

    return {"message": "Password updated. You can sign in now."}
