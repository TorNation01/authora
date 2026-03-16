"""Invite accept endpoint tests - expiry, revoke, email match, idempotency."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from authora.models import Project, ProjectInvite, ProjectMember, User
from authora.services.auth import hash_password


@pytest.fixture
async def inviter(db):
    """Create inviter (project owner) - different from test_user."""
    inviter = User(
        email="owner@example.com",
        hashed_password=hash_password("ownerpass"),
        display_name="Owner",
        is_active=True,
    )
    db.add(inviter)
    await db.flush()
    return inviter


@pytest.fixture
async def project(db, inviter):
    """Project owned by inviter."""
    proj = Project(name="Shared Project", user_id=inviter.id)
    db.add(proj)
    await db.flush()
    return proj


@pytest.fixture
async def pending_invite(db, project, inviter):
    """Pending invite for test_user (test@example.com)."""
    import secrets

    invite = ProjectInvite(
        email="test@example.com",
        project_id=project.id,
        role="beta_reader",
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        invited_by=inviter.id,
    )
    db.add(invite)
    await db.flush()
    return invite


@pytest.mark.asyncio
async def test_accept_invite_success(auth_client, db, project, pending_invite, test_user):
    """Accept valid invite creates member and updates invite status."""
    resp = await auth_client.post(
        "/api/v1/invites/accept",
        json={"token": pending_invite.token},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == str(test_user.id)
    assert data["project_id"] == str(project.id)
    assert data["role"] == "beta_reader"

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == test_user.id,
        )
    )
    member = result.scalar_one()
    assert member.role == "beta_reader"

    result = await db.execute(select(ProjectInvite).where(ProjectInvite.id == pending_invite.id))
    invite = result.scalar_one()
    assert invite.status == "accepted"


@pytest.mark.asyncio
async def test_accept_invite_expired(auth_client, db, project, inviter):
    """Expired invite returns 400 and marks invite expired."""
    import secrets

    invite = ProjectInvite(
        email="test@example.com",
        project_id=project.id,
        role="beta_reader",
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        invited_by=inviter.id,
    )
    db.add(invite)
    await db.flush()

    resp = await auth_client.post("/api/v1/invites/accept", json={"token": invite.token})
    assert resp.status_code == 400
    assert "expired" in resp.json().get("detail", "").lower()

    await db.refresh(invite)
    assert invite.status == "expired"


@pytest.mark.asyncio
async def test_accept_invite_revoked(auth_client, db, project, pending_invite):
    """Revoked invite returns 400."""
    pending_invite.status = "revoked"
    await db.flush()

    resp = await auth_client.post(
        "/api/v1/invites/accept",
        json={"token": pending_invite.token},
    )
    assert resp.status_code == 400
    assert "no longer valid" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_accept_invite_wrong_email(auth_client, db, project, inviter):
    """User with non-matching email gets 403."""
    import secrets

    invite = ProjectInvite(
        email="other@example.com",
        project_id=project.id,
        role="beta_reader",
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        invited_by=inviter.id,
    )
    db.add(invite)
    await db.flush()

    resp = await auth_client.post("/api/v1/invites/accept", json={"token": invite.token})
    assert resp.status_code == 403
    assert "email" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_accept_invite_already_member(auth_client, db, project, pending_invite, test_user):
    """Already a member gets 400."""
    member = ProjectMember(
        user_id=test_user.id,
        project_id=project.id,
        role="viewer",
        invited_by=None,
    )
    db.add(member)
    await db.flush()

    resp = await auth_client.post(
        "/api/v1/invites/accept",
        json={"token": pending_invite.token},
    )
    assert resp.status_code == 400
    assert "already a member" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_accept_invite_invalid_token(auth_client):
    """Invalid token returns 404."""
    resp = await auth_client.post(
        "/api/v1/invites/accept",
        json={"token": "invalid-token-xyz"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_accept_invite_requires_auth(anon_client):
    """Accept requires authentication."""
    resp = await anon_client.post(
        "/api/v1/invites/accept",
        json={"token": "any-token"},
    )
    assert resp.status_code == 401
