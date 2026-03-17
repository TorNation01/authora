"""Community models: writing groups, feedback threads, optional public profiles."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.project import Project
    from authora.models.user import User

# Profile visibility: private (default), friends_only (group members), public
PROFILE_VISIBILITY_VALUES = ("private", "friends_only", "public")

# Feedback target types (for FeedbackThread)
FEEDBACK_TARGET_TYPES = ("chapter", "shared_excerpt", "project")


class WritingGroup(Base):
    """Writing group: optional community for writers to share progress and feedback."""

    __tablename__ = "writing_groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    members: Mapped[list["WritingGroupMember"]] = relationship(
        "WritingGroupMember", back_populates="group", cascade="all, delete-orphan"
    )
    invites: Mapped[list["WritingGroupInvite"]] = relationship(
        "WritingGroupInvite", back_populates="group", cascade="all, delete-orphan"
    )


class WritingGroupMember(Base):
    """Membership in a writing group."""

    __tablename__ = "writing_group_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writing_groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")  # admin, member
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group: Mapped["WritingGroup"] = relationship("WritingGroup", back_populates="members")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


class WritingGroupInvite(Base):
    """Invitation to join a writing group."""

    __tablename__ = "writing_group_invites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writing_groups.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    invited_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group: Mapped["WritingGroup"] = relationship("WritingGroup", back_populates="invites")
    inviter: Mapped["User"] = relationship("User", foreign_keys=[invited_by_id])


class FeedbackThread(Base):
    """Feedback thread on shared content (chapter, excerpt)."""

    __tablename__ = "feedback_threads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="feedback_threads")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    comments: Mapped[list["FeedbackComment"]] = relationship(
        "FeedbackComment", back_populates="thread", cascade="all, delete-orphan"
    )


class FeedbackComment(Base):
    """Comment in a feedback thread."""

    __tablename__ = "feedback_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback_threads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    thread: Mapped["FeedbackThread"] = relationship("FeedbackThread", back_populates="comments")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
