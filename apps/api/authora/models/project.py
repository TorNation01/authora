"""Project model."""

import uuid

GUIDANCE_MODES = ("guided", "flexible", "freeform")
KNOWLEDGE_MODES = ("fiction", "nonfiction", "memoir", "workbook", "hybrid")
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book
    from authora.models.integrity import IntegrityIssue, IntegrityScan
    from authora.models.collaboration import (
        CollaborationActivity,
        ProjectInvite,
        ProjectMember,
        ProjectShare,
    )
    from authora.models.note import Note
    from authora.models.project_template import ProjectTemplate
    from authora.models.revision_pass import RevisionPass
    from authora.models.user import User


class Project(Base):
    """Writing project (container for books)."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_templates.id", ondelete="SET NULL"), nullable=True
    )
    guidance_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="guided")
    knowledge_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="fiction")
    knowledge_modules: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="projects")
    template: Mapped["ProjectTemplate | None"] = relationship("ProjectTemplate", foreign_keys=[template_id])
    books: Mapped[list["Book"]] = relationship("Book", back_populates="project", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="project", cascade="all, delete-orphan")
    revision_passes: Mapped[list["RevisionPass"]] = relationship(
        "RevisionPass", back_populates="project", cascade="all, delete-orphan"
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )
    invites: Mapped[list["ProjectInvite"]] = relationship(
        "ProjectInvite", back_populates="project", cascade="all, delete-orphan"
    )
    shares: Mapped[list["ProjectShare"]] = relationship(
        "ProjectShare", back_populates="project", cascade="all, delete-orphan"
    )
    collaboration_activities: Mapped[list["CollaborationActivity"]] = relationship(
        "CollaborationActivity", back_populates="project", cascade="all, delete-orphan"
    )
    ideas: Mapped[list["Idea"]] = relationship(
        "Idea", back_populates="project", cascade="all, delete-orphan"
    )
    research_entries: Mapped[list["ResearchEntry"]] = relationship(
        "ResearchEntry", back_populates="project", cascade="all, delete-orphan"
    )
    vault_characters: Mapped[list["VaultCharacter"]] = relationship(
        "VaultCharacter", back_populates="project", cascade="all, delete-orphan"
    )
    vault_locations: Mapped[list["VaultLocation"]] = relationship(
        "VaultLocation", back_populates="project", cascade="all, delete-orphan"
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        "TimelineEvent", back_populates="project", cascade="all, delete-orphan"
    )
    vault_relationships: Mapped[list["VaultRelationship"]] = relationship(
        "VaultRelationship", back_populates="project", cascade="all, delete-orphan"
    )
    vault_themes: Mapped[list["Theme"]] = relationship(
        "Theme", back_populates="project", cascade="all, delete-orphan"
    )
    vault_sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="project", cascade="all, delete-orphan"
    )
    integrity_scans: Mapped[list["IntegrityScan"]] = relationship(
        "IntegrityScan", back_populates="project", cascade="all, delete-orphan"
    )
    integrity_issues: Mapped[list["IntegrityIssue"]] = relationship(
        "IntegrityIssue", back_populates="project", cascade="all, delete-orphan"
    )
