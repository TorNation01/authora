"""Add notes, research, and idea capture system

Revision ID: 011
Revises: 010
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add project_id to notes (for general notebook)
    op.add_column("notes", sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(
        "UPDATE notes SET project_id = (SELECT project_id FROM books WHERE books.id = notes.book_id)"
    )
    op.alter_column("notes", "project_id", nullable=False)
    op.create_foreign_key("fk_notes_project", "notes", "projects", ["project_id"], ["id"], ondelete="CASCADE")

    # Make book_id nullable for project-level notes
    op.alter_column(
        "notes",
        "book_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )

    # Extend notes with new fields
    op.add_column("notes", sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("notes", sa.Column("note_type", sa.String(50), nullable=False, server_default="general"))
    op.add_column("notes", sa.Column("source", sa.String(500), nullable=True))
    op.add_column("notes", sa.Column("source_url", sa.String(1000), nullable=True))
    op.add_column("notes", sa.Column("pinned", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("notes", sa.Column("is_inspiration", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("notes", sa.Column("category", sa.String(100), nullable=True))
    op.add_column("notes", sa.Column("tags", postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")))
    op.add_column("notes", sa.Column("voice_note_placeholder", postgresql.JSONB(), nullable=True))
    op.add_column("notes", sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))
    op.create_foreign_key("fk_notes_chapter", "notes", "chapters", ["chapter_id"], ["id"], ondelete="SET NULL")

    # Note attachments
    op.create_table(
        "note_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_note_attachments_note_id", "note_attachments", ["note_id"])

    # Full-text search index
    op.execute("""
        CREATE INDEX ix_notes_search ON notes USING GIN (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'')))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_notes_search")
    op.drop_index("ix_note_attachments_note_id", table_name="note_attachments")
    op.drop_table("note_attachments")
    op.drop_constraint("fk_notes_chapter", "notes", type_="foreignkey")
    op.drop_column("notes", "sort_order")
    op.drop_column("notes", "voice_note_placeholder")
    op.drop_column("notes", "tags")
    op.drop_column("notes", "category")
    op.drop_column("notes", "is_inspiration")
    op.drop_column("notes", "pinned")
    op.drop_column("notes", "source_url")
    op.drop_column("notes", "source")
    op.drop_column("notes", "note_type")
    op.drop_column("notes", "chapter_id")
    op.alter_column("notes", "book_id", nullable=False)
    op.drop_constraint("fk_notes_project", "notes", type_="foreignkey")
    op.drop_column("notes", "project_id")
