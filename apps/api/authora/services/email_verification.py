"""Proof-of-inbox: issue, deliver and consume email verification links.

Design notes
------------
* The raw token only ever exists in the email and in memory. The database holds
  a SHA-256 of it, so a dump cannot be replayed into account takeovers.
* Tokens are single use: consuming one clears the hash in the same commit.
* A token lives 48 hours. Reissuing replaces the previous one, so an old link
  stops working the moment a new email is sent.
* Verification is a *soft* gate: an unverified account can sign in and write,
  but cannot check out. Locking people out of a product they just signed up for
  to teach them a security lesson is how you lose the customer and keep the bot.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models.user import User

TOKEN_TTL_HOURS = 48
RESEND_COOLDOWN_SECONDS = 300  # one mail per five minutes per account


def _hash(token: str) -> str:
    return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()


def verification_url(token: str) -> str:
    base = (get_settings().app_base_url or "https://authora.studio").rstrip("/")
    return f"{base}/verify-email?token={token}"


async def issue_verification(db: AsyncSession, user: User, *, force: bool = False) -> str | None:
    """Create a fresh token for ``user`` and return the raw value.

    Returns None when the address is already verified, or when a mail went out
    less than five minutes ago and ``force`` is not set — the caller should keep
    quiet rather than let the endpoint be used as a mail cannon.
    """
    now = datetime.now(timezone.utc)

    if user.email_verified and not force:
        return None

    sent_at = user.email_verification_sent_at
    if sent_at is not None and not force:
        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        if now - sent_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS):
            return None

    token = secrets.token_urlsafe(32)
    user.email_verification_token_hash = _hash(token)
    user.email_verification_sent_at = now
    await db.flush()
    return token


def is_verification_expired(user: User) -> bool:
    sent_at = user.email_verification_sent_at
    if sent_at is None:
        return True
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - sent_at > timedelta(hours=TOKEN_TTL_HOURS)


async def consume_verification(db: AsyncSession, token: str) -> User | None:
    """Mark the matching account verified. Returns the user, or None."""
    token = (token or "").strip()
    if len(token) < 16:
        return None

    result = await db.execute(
        select(User).where(User.email_verification_token_hash == _hash(token)).limit(1)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None

    if is_verification_expired(user):
        # Burn it: an expired link must not keep working if the clock is nudged.
        user.email_verification_token_hash = None
        await db.flush()
        return None

    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    user.email_verification_token_hash = None
    await db.flush()
    return user


def mark_verified(user: User) -> None:
    """Use when ownership of the inbox has been proved some other way (reset link)."""
    if user.email_verified:
        return
    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    user.email_verification_token_hash = None
