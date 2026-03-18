"""Zotero connection and sync models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.user import User
    from authora.models.vault import Source


class ZoteroConnection(Base):
    """User's Zotero library connection (API key, library type, library ID)."""

    __tablename__ = "zotero_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    library_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user | group
    library_id: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_version: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    sync_error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="zotero_connections")
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="zotero_connection")
