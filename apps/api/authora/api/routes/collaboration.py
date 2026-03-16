"""Collaboration API routes: invites, members, shares, approvals, activity."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import (
    get_book_in_project_or_404,
    get_chapter_or_404,
    get_project_with_access_or_404,
)
from authora.database import get_db
from authora.models import (
    ChapterApproval,
    CollaborationActivity,
    ProjectInvite,
    ProjectMember,
    ProjectShare,
    User,
)
from authora.models.collaboration import (
    PERMISSION_APPROVE_CHAPTERS,
    PERMISSION_MANAGE_INVITES,
    PERMISSION_MANAGE_MEMBERS,
    PERMISSION_MANAGE_SHARES,
    PERMISSION_VIEW_ACTIVITY,
    PERMISSION_VIEW_MANUSCRIPT,
    has_permission,
)
from authora.schemas.collaboration import (
    ChapterApprovalResponse,
    ChapterApprovalUpdate,
    CollaborationActivityResponse,
    ProjectInviteCreate,
    ProjectInviteResponse,
    ProjectMemberResponse,
    ProjectShareCreate,
    ProjectShareResponse,
)

router = APIRouter(prefix="/projects/{project_id}", tags=["collaboration"])

# Standalone invite routes (no project_id in path)
invite_router = APIRouter(prefix="/invites", tags=["collaboration"])


def _require_permission(role: str, permission: str) -> None:
    """Raise 403 if role lacks permission."""
    if not has_permission(role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


# --- Invites ---


@router.get("/invites", response_model=list[ProjectInviteResponse])
async def list_invites(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(None, alias="status", description="pending | accepted | expired | revoked"),
):
    """List project invites. Requires manage_invites or owner."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_INVITES)

    q = select(ProjectInvite).where(ProjectInvite.project_id == project_id)
    if status_filter:
        q = q.where(ProjectInvite.status == status_filter)
    q = q.order_by(ProjectInvite.created_at.desc())
    result = await db.execute(q)
    return [ProjectInviteResponse.model_validate(i) for i in result.scalars().all()]


@router.post("/invites", response_model=ProjectInviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    project_id: uuid.UUID,
    data: ProjectInviteCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create project invite. Requires manage_invites or owner."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_INVITES)

    # Check for existing member or pending invite
    user_result = await db.execute(select(User).where(User.email == data.email))
    existing_user = user_result.scalar_one_or_none()
    if existing_user:
        member_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == existing_user.id,
            )
        )
        if member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member",
            )
    invite_result = await db.execute(
        select(ProjectInvite).where(
            ProjectInvite.project_id == project_id,
            ProjectInvite.email == data.email,
            ProjectInvite.status == "pending",
        )
    )
    if invite_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already pending for this email",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    invite = ProjectInvite(
        email=data.email,
        project_id=project_id,
        role=data.role,
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=expires_at,
        invited_by=current_user.id,
    )
    db.add(invite)
    await db.flush()

    activity = CollaborationActivity(
        project_id=project_id,
        user_id=current_user.id,
        action="invite_created",
        entity_type="invite",
        entity_id=str(invite.id),
        extra_data={"email": data.email, "role": data.role},
    )
    db.add(activity)

    await db.refresh(invite)
    return ProjectInviteResponse.model_validate(invite)


@router.post("/invites/{invite_id}/resend", response_model=ProjectInviteResponse)
async def resend_invite(
    project_id: uuid.UUID,
    invite_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resend invite (new token, extended expiry). Requires manage_invites."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_INVITES)

    result = await db.execute(
        select(ProjectInvite).where(
            ProjectInvite.id == invite_id,
            ProjectInvite.project_id == project_id,
        )
    )
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if invite.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only resend pending invites",
        )

    invite.token = secrets.token_urlsafe(32)
    invite.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.flush()
    await db.refresh(invite)
    return ProjectInviteResponse.model_validate(invite)


@router.post("/invites/{invite_id}/revoke", response_model=ProjectInviteResponse)
async def revoke_invite(
    project_id: uuid.UUID,
    invite_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Revoke invite. Requires manage_invites."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_INVITES)

    result = await db.execute(
        select(ProjectInvite).where(
            ProjectInvite.id == invite_id,
            ProjectInvite.project_id == project_id,
        )
    )
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    invite.status = "revoked"
    await db.flush()
    await db.refresh(invite)
    return ProjectInviteResponse.model_validate(invite)


# --- Members ---


@router.get("/members", response_model=list[ProjectMemberResponse])
async def list_members(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List project members with user info. Owner sees all; members need manage_members for full list."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_MEMBERS)

    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.joined_at)
    )
    members = result.scalars().all()
    return [
        ProjectMemberResponse.model_validate(m).model_copy(
            update={
                "email": m.user.email if m.user else None,
                "display_name": m.user.display_name if m.user else None,
            }
        )
        for m in members
    ]


@router.get("/members/{member_id}", response_model=ProjectMemberResponse)
async def get_member(
    project_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a project member by ID."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_MEMBERS)

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return ProjectMemberResponse.model_validate(member)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a member from the project. Requires manage_members. Cannot remove owner."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_MEMBERS)

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove project owner",
        )

    await db.delete(member)

    activity = CollaborationActivity(
        project_id=project_id,
        user_id=current_user.id,
        action="member_removed",
        entity_type="member",
        entity_id=str(member_id),
        extra_data={"user_id": str(member.user_id)},
    )
    db.add(activity)


# --- Shares ---


@router.get("/shares", response_model=list[ProjectShareResponse])
async def list_shares(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List project shares. Requires manage_shares."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_SHARES)

    result = await db.execute(
        select(ProjectShare).where(ProjectShare.project_id == project_id).order_by(ProjectShare.created_at.desc())
    )
    return [ProjectShareResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/shares", response_model=ProjectShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share(
    project_id: uuid.UUID,
    data: ProjectShareCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create project share. Requires manage_shares."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_MANAGE_SHARES)

    if data.share_scope == "chapters" and (not data.chapter_ids or len(data.chapter_ids) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="chapter_ids required for chapters scope",
        )
    if not data.shared_with_user_id and not data.shared_with_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="shared_with_user_id or shared_with_email required",
        )

    chapter_ids_json = [str(c) for c in data.chapter_ids] if data.chapter_ids else None
    share = ProjectShare(
        project_id=project_id,
        share_scope=data.share_scope,
        chapter_ids=chapter_ids_json,
        shared_with_user_id=data.shared_with_user_id,
        shared_with_email=data.shared_with_email,
        created_by=current_user.id,
    )
    db.add(share)
    await db.flush()
    await db.refresh(share)
    return ProjectShareResponse.model_validate(share)


# --- Chapter approval (under books path) ---


@router.get(
    "/books/{book_id}/approvals",
    response_model=list[ChapterApprovalResponse],
)
async def list_chapter_approvals(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all chapter approvals for a book. Requires view_manuscript or approve_chapters."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    if not (has_permission(role, PERMISSION_APPROVE_CHAPTERS) or has_permission(role, PERMISSION_VIEW_MANUSCRIPT)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    await get_book_in_project_or_404(db, book_id, project_id)
    from authora.models import Chapter

    result = await db.execute(
        select(ChapterApproval)
        .join(Chapter, ChapterApproval.chapter_id == Chapter.id)
        .where(Chapter.book_id == book_id)
        .order_by(Chapter.sort_order)
    )
    return [ChapterApprovalResponse.model_validate(a) for a in result.scalars().all()]


@router.get(
    "/books/{book_id}/chapters/{chapter_id}/approval",
    response_model=ChapterApprovalResponse | None,
)
async def get_chapter_approval(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get chapter approval status. Requires approve_chapters or view_manuscript."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    if not (has_permission(role, PERMISSION_APPROVE_CHAPTERS) or has_permission(role, PERMISSION_VIEW_MANUSCRIPT)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    await get_book_in_project_or_404(db, book_id, project_id)
    chapter = await get_chapter_or_404(db, book_id, chapter_id)

    result = await db.execute(
        select(ChapterApproval).where(ChapterApproval.chapter_id == chapter.id)
    )
    approval = result.scalar_one_or_none()
    if not approval:
        return None
    return ChapterApprovalResponse.model_validate(approval)


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/approval",
    response_model=ChapterApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chapter_approval(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create chapter approval (pending). Requires approve_chapters."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_APPROVE_CHAPTERS)

    await get_book_in_project_or_404(db, book_id, project_id)
    chapter = await get_chapter_or_404(db, book_id, chapter_id)

    result = await db.execute(
        select(ChapterApproval).where(ChapterApproval.chapter_id == chapter.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval already exists for this chapter",
        )

    approval = ChapterApproval(
        chapter_id=chapter.id,
        status="pending",
    )
    db.add(approval)
    await db.flush()

    activity = CollaborationActivity(
        project_id=project_id,
        user_id=current_user.id,
        action="approval_created",
        entity_type="chapter_approval",
        entity_id=str(approval.id),
        extra_data={"chapter_id": str(chapter.id)},
    )
    db.add(activity)

    await db.refresh(approval)
    return ChapterApprovalResponse.model_validate(approval)


@router.patch(
    "/books/{book_id}/chapters/{chapter_id}/approval",
    response_model=ChapterApprovalResponse,
)
async def update_chapter_approval(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterApprovalUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update chapter approval status. Requires approve_chapters."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_APPROVE_CHAPTERS)

    await get_book_in_project_or_404(db, book_id, project_id)
    chapter = await get_chapter_or_404(db, book_id, chapter_id)

    result = await db.execute(
        select(ChapterApproval).where(ChapterApproval.chapter_id == chapter.id)
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    approval.status = data.status
    if data.notes is not None:
        approval.notes = data.notes
    if data.status in ("approved", "rejected", "changes_requested"):
        approval.approved_by = current_user.id
        approval.approved_at = datetime.now(timezone.utc)

    await db.flush()

    activity = CollaborationActivity(
        project_id=project_id,
        user_id=current_user.id,
        action="approval_updated",
        entity_type="chapter_approval",
        entity_id=str(approval.id),
        extra_data={"status": data.status, "chapter_id": str(chapter.id)},
    )
    db.add(activity)

    await db.refresh(approval)
    return ChapterApprovalResponse.model_validate(approval)


# --- Activity ---


@router.get("/activity", response_model=list[CollaborationActivityResponse])
async def list_activity(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List project collaboration activity. Requires view_activity."""
    project, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_permission(role, PERMISSION_VIEW_ACTIVITY)

    result = await db.execute(
        select(CollaborationActivity)
        .where(CollaborationActivity.project_id == project_id)
        .order_by(CollaborationActivity.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [CollaborationActivityResponse.model_validate(a) for a in result.scalars().all()]
