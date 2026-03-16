"""Collaboration models: members, invites, shares, approvals, activity."""

import uuid

# Permission constants
PERMISSION_VIEW_MANUSCRIPT = "view_manuscript"
PERMISSION_EDIT_MANUSCRIPT = "edit_manuscript"
PERMISSION_COMMENT = "comment"
PERMISSION_VIEW_NOTES = "view_notes"
PERMISSION_EDIT_NOTES = "edit_notes"
PERMISSION_APPROVE_CHAPTERS = "approve_chapters"
PERMISSION_MANAGE_INVITES = "manage_invites"
PERMISSION_MANAGE_MEMBERS = "manage_members"
PERMISSION_MANAGE_SHARES = "manage_shares"
PERMISSION_DELETE_PROJECT = "delete_project"
PERMISSION_VIEW_ACTIVITY = "view_activity"

# Role -> permissions mapping
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "owner": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_EDIT_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_EDIT_NOTES,
        PERMISSION_APPROVE_CHAPTERS,
        PERMISSION_MANAGE_INVITES,
        PERMISSION_MANAGE_MEMBERS,
        PERMISSION_MANAGE_SHARES,
        PERMISSION_DELETE_PROJECT,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "admin": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_EDIT_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_EDIT_NOTES,
        PERMISSION_APPROVE_CHAPTERS,
        PERMISSION_MANAGE_INVITES,
        PERMISSION_MANAGE_MEMBERS,
        PERMISSION_MANAGE_SHARES,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "editor": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_EDIT_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_EDIT_NOTES,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "co_writer": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_EDIT_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_EDIT_NOTES,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "beta_reader": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "reviewer": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_APPROVE_CHAPTERS,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "client": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_COMMENT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_APPROVE_CHAPTERS,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "viewer": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_VIEW_NOTES,
        PERMISSION_VIEW_ACTIVITY,
    }),
    "guest": frozenset({
        PERMISSION_VIEW_MANUSCRIPT,
        PERMISSION_COMMENT,
    }),
}


def has_permission(role: str, permission: str) -> bool:
    """Check if role has the given permission."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

# Role enum values stored as strings
COLLABORATION_ROLES = (
    "owner",
    "admin",
    "editor",
    "beta_reader",
    "reviewer",
    "client",
    "co_writer",
    "viewer",
    "guest",
)

# Share scope values
PROJECT_SHARE_SCOPES = ("full_project", "manuscript", "chapters", "review_copy")

# Invite status values
INVITE_STATUSES = ("pending", "accepted", "expired", "revoked")

# Chapter approval status values
CHAPTER_APPROVAL_STATUSES = ("pending", "approved", "rejected", "changes_requested")

if TYPE_CHECKING:
    from authora.models.book import Chapter
    from authora.models.project import Project
    from authora.models.user import User


class ProjectMember(Base):
    """Project membership: user_id, project_id, role, invited_by, joined_at."""

    __tablename__ = "project_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    inviter: Mapped["User | None"] = relationship("User", foreign_keys=[invited_by])


class ProjectInvite(Base):
    """Invitation to join project by email."""

    __tablename__ = "project_invites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="invites")
    inviter: Mapped["User"] = relationship("User", foreign_keys=[invited_by])


class ProjectShare(Base):
    """Share scope: full_project, manuscript, chapters, review_copy; includes chapter_ids JSONB."""

    __tablename__ = "project_shares"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    share_scope: Mapped[str] = mapped_column(String(50), nullable=False)
    chapter_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # list of UUID strings for chapters scope
    shared_with_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    shared_with_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="shares")
    shared_with_user: Mapped["User | None"] = relationship("User", foreign_keys=[shared_with_user_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])


class ChapterApproval(Base):
    """Chapter approval: chapter_id, status, approved_by, approved_at."""

    __tablename__ = "chapter_approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="approval")
    approver: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by])


class CollaborationActivity(Base):
    """Project activity log: project_id, user_id, action, entity_type, entity_id, metadata JSONB."""

    __tablename__ = "collaboration_activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="collaboration_activities")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
