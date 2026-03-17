"""Community API routes: optional public profiles, writing groups, feedback threads.

Fully optional, privacy-first. All features require explicit opt-in.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_project_with_access_or_404
from authora.database import get_db
from authora.models import Book, Chapter, Profile, Project, User, UserPreference
from authora.models.community import (
    FEEDBACK_TARGET_TYPES,
    PROFILE_VISIBILITY_VALUES,
    FeedbackComment,
    FeedbackThread,
    WritingGroup,
    WritingGroupInvite,
    WritingGroupMember,
)
from authora.schemas.community import (
    CommunitySettingsResponse,
    CommunitySettingsUpdate,
    FeedbackCommentCreate,
    FeedbackCommentResponse,
    FeedbackThreadCreate,
    FeedbackThreadResponse,
    ProgressShareResponse,
    PublicProfileResponse,
    WritingGroupCreate,
    WritingGroupInviteCreate,
    WritingGroupResponse,
)

router = APIRouter(prefix="/community", tags=["community"])


def _get_community_prefs(prefs: UserPreference | None) -> dict:
    """Get community preferences from user preferences JSONB."""
    if not prefs or not prefs.preferences:
        return {}
    return prefs.preferences.get("community", {}) or {}


# --- Settings ---

@router.get("/settings", response_model=CommunitySettingsResponse)
async def get_community_settings(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current user's community settings. All optional, defaults private."""
    profile = await db.get(Profile, current_user.id)
    prefs = await db.get(UserPreference, current_user.id)
    community = _get_community_prefs(prefs)
    return CommunitySettingsResponse(
        profile_visibility=profile.profile_visibility if profile else "private",
        profile_slug=profile.profile_slug if profile else None,
        share_progress=community.get("share_progress", False),
    )


@router.patch("/settings", response_model=CommunitySettingsResponse)
async def update_community_settings(
    data: CommunitySettingsUpdate,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update community settings. All optional."""
    profile = await db.get(Profile, current_user.id)
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        await db.flush()
    if data.profile_visibility is not None:
        if data.profile_visibility not in PROFILE_VISIBILITY_VALUES:
            raise HTTPException(status_code=400, detail="Invalid profile_visibility")
        profile.profile_visibility = data.profile_visibility
    if data.profile_slug is not None:
        slug = data.profile_slug.strip().lower() if data.profile_slug else None
        if slug:
            existing = await db.execute(
                select(Profile).where(Profile.profile_slug == slug, Profile.user_id != current_user.id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Profile slug already taken")
        profile.profile_slug = slug
    prefs = await db.get(UserPreference, current_user.id)
    if not prefs:
        prefs = UserPreference(user_id=current_user.id, preferences={})
        db.add(prefs)
        await db.flush()
    if data.share_progress is not None:
        community = prefs.preferences.get("community", {}) or {}
        community["share_progress"] = data.share_progress
        prefs.preferences = {**prefs.preferences, "community": community}
    await db.flush()
    await db.refresh(profile)
    community = _get_community_prefs(prefs)
    return CommunitySettingsResponse(
        profile_visibility=profile.profile_visibility,
        profile_slug=profile.profile_slug,
        share_progress=community.get("share_progress", False),
    )


# --- Public profile (only when visibility allows) ---

@router.get("/profiles/{slug}", response_model=PublicProfileResponse)
async def get_public_profile(
    slug: str,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get public profile by slug. Returns 404 if profile is private."""
    result = await db.execute(
        select(Profile, User).join(User, Profile.user_id == User.id).where(Profile.profile_slug == slug)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile, user = row
    if profile.profile_visibility != "public":
        raise HTTPException(status_code=404, detail="Profile not found")
    return PublicProfileResponse(
        id=user.id,
        display_name=user.display_name,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        profile_slug=profile.profile_slug,
    )


@router.get("/profiles/{slug}/progress", response_model=ProgressShareResponse)
async def get_shared_progress(
    slug: str,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get shared progress by profile slug. Only when user opts in."""
    result = await db.execute(
        select(Profile, User, UserPreference)
        .join(User, Profile.user_id == User.id)
        .outerjoin(UserPreference, UserPreference.user_id == User.id)
        .where(Profile.profile_slug == slug)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile, user, prefs = row
    community = _get_community_prefs(prefs)
    if not community.get("share_progress"):
        raise HTTPException(status_code=404, detail="Progress not shared")
    if profile.profile_visibility != "public" and profile.profile_visibility != "friends_only":
        raise HTTPException(status_code=404, detail="Progress not shared")
    # Compute stats (exclude deleted projects)
    total_words = await db.scalar(
        select(func.coalesce(func.sum(Chapter.word_count), 0)).select_from(Chapter).join(Book).join(Project).where(
            Project.user_id == user.id, Project.deleted_at.is_(None)
        )
    ) or 0
    total_books = await db.scalar(
        select(func.count(Book.id)).select_from(Book).join(Project).where(
            Project.user_id == user.id, Project.deleted_at.is_(None)
        )
    ) or 0
    total_chapters = await db.scalar(
        select(func.count(Chapter.id)).select_from(Chapter).join(Book).join(Project).where(
            Project.user_id == user.id, Project.deleted_at.is_(None)
        )
    ) or 0
    return ProgressShareResponse(
        total_words=int(total_words),
        total_books=int(total_books),
        total_chapters=int(total_chapters),
    )


# --- Writing groups ---

@router.get("/groups", response_model=list[WritingGroupResponse])
async def list_my_groups(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List writing groups the current user is a member of."""
    result = await db.execute(
        select(WritingGroup, func.count(WritingGroupMember.id).label("member_count"))
        .join(WritingGroupMember, WritingGroupMember.group_id == WritingGroup.id)
        .where(WritingGroupMember.user_id == current_user.id)
        .group_by(WritingGroup.id)
    )
    rows = result.all()
    return [
        WritingGroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            created_by_id=g.created_by_id,
            is_public=g.is_public,
            member_count=member_count,
            created_at=g.created_at,
        )
        for g, member_count in rows
    ]


@router.post("/groups", response_model=WritingGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_writing_group(
    data: WritingGroupCreate,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a writing group."""
    group = WritingGroup(
        name=data.name,
        description=data.description,
        created_by_id=current_user.id,
        is_public=data.is_public,
    )
    db.add(group)
    await db.flush()
    member = WritingGroupMember(group_id=group.id, user_id=current_user.id, role="admin")
    db.add(member)
    await db.flush()
    await db.refresh(group)
    return WritingGroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by_id=group.created_by_id,
        is_public=group.is_public,
        member_count=1,
        created_at=group.created_at,
    )


@router.post("/groups/{group_id}/invite", status_code=status.HTTP_201_CREATED)
async def invite_to_group(
    group_id: uuid.UUID,
    data: WritingGroupInviteCreate,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Invite user to writing group by email."""
    group = await db.get(WritingGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    member_result = await db.execute(
        select(WritingGroupMember).where(
            WritingGroupMember.group_id == group_id,
            WritingGroupMember.user_id == current_user.id,
        )
    )
    member = member_result.scalar_one_or_none()
    if not member or member.role != "admin":
        raise HTTPException(status_code=403, detail="Not a group admin")
    invite = WritingGroupInvite(
        group_id=group_id,
        email=data.email.strip().lower(),
        invited_by_id=current_user.id,
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    await db.flush()
    return {"invite_id": str(invite.id), "expires_at": invite.expires_at.isoformat()}


# --- Feedback threads (project-scoped) ---

@router.get("/projects/{project_id}/feedback", response_model=list[FeedbackThreadResponse])
async def list_feedback_threads(
    project_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List feedback threads for a project."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(FeedbackThread, func.count(FeedbackComment.id).label("comment_count"))
        .outerjoin(FeedbackComment, FeedbackComment.thread_id == FeedbackThread.id)
        .where(FeedbackThread.project_id == project_id)
        .group_by(FeedbackThread.id)
        .order_by(FeedbackThread.created_at.desc())
    )
    rows = result.all()
    return [
        FeedbackThreadResponse(
            id=t.id,
            project_id=t.project_id,
            target_type=t.target_type,
            target_id=t.target_id,
            title=t.title,
            created_by_id=t.created_by_id,
            comment_count=comment_count,
            created_at=t.created_at,
        )
        for t, comment_count in rows
    ]


@router.post("/projects/{project_id}/feedback", response_model=FeedbackThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_thread(
    project_id: uuid.UUID,
    data: FeedbackThreadCreate,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create feedback thread on project content."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    if data.target_type not in FEEDBACK_TARGET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid target_type")
    thread = FeedbackThread(
        project_id=project_id,
        target_type=data.target_type,
        target_id=data.target_id,
        title=data.title,
        created_by_id=current_user.id,
    )
    db.add(thread)
    await db.flush()
    await db.refresh(thread)
    return FeedbackThreadResponse(
        id=thread.id,
        project_id=thread.project_id,
        target_type=thread.target_type,
        target_id=thread.target_id,
        title=thread.title,
        created_by_id=thread.created_by_id,
        comment_count=0,
        created_at=thread.created_at,
    )


@router.get("/projects/{project_id}/feedback/{thread_id}/comments", response_model=list[FeedbackCommentResponse])
async def list_feedback_comments(
    project_id: uuid.UUID,
    thread_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List comments in a feedback thread."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    thread = await db.get(FeedbackThread, thread_id)
    if not thread or thread.project_id != project_id:
        raise HTTPException(status_code=404, detail="Thread not found")
    result = await db.execute(
        select(FeedbackComment).where(FeedbackComment.thread_id == thread_id).order_by(FeedbackComment.created_at)
    )
    return [FeedbackCommentResponse.model_validate(c) for c in result.scalars().all()]


@router.post(
    "/projects/{project_id}/feedback/{thread_id}/comments",
    response_model=FeedbackCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback_comment(
    project_id: uuid.UUID,
    thread_id: uuid.UUID,
    data: FeedbackCommentCreate,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add comment to feedback thread."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    thread = await db.get(FeedbackThread, thread_id)
    if not thread or thread.project_id != project_id:
        raise HTTPException(status_code=404, detail="Thread not found")
    comment = FeedbackComment(
        thread_id=thread_id,
        user_id=current_user.id,
        body=data.body.strip(),
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return FeedbackCommentResponse.model_validate(comment)
