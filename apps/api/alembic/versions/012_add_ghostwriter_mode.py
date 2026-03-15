"""Add ghostwriter mode - workspace, briefs, content provenance

Revision ID: 012
Revises: 011
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ghostwriter_workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mode", sa.String(50), nullable=False, server_default="heavy"),
        sa.Column("workflow_step", sa.String(50), nullable=False, server_default="intake"),
        sa.Column("intake_answers", postgresql.JSONB(), nullable=True),
        sa.Column("voice_tone", sa.String(255), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("desired_outcome", sa.Text(), nullable=True),
        sa.Column("outline", postgresql.JSONB(), nullable=True),
        sa.Column("outline_approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("book_id"),
    )
    op.create_index("ix_ghostwriter_workspaces_book_id", "ghostwriter_workspaces", ["book_id"])

    op.create_table(
        "chapter_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ghostwriter_workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["ghostwriter_workspace_id"], ["ghostwriter_workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_briefs_chapter_id", "chapter_briefs", ["chapter_id"])
    op.create_index("ix_chapter_briefs_ghostwriter_workspace_id", "chapter_briefs", ["ghostwriter_workspace_id"])

    op.add_column("chapters", sa.Column("content_source", sa.String(50), nullable=True))
    op.add_column("chapter_versions", sa.Column("content_source", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("chapter_versions", "content_source")
    op.drop_column("chapters", "content_source")
    op.drop_index("ix_chapter_briefs_ghostwriter_workspace_id", table_name="chapter_briefs")
    op.drop_index("ix_chapter_briefs_chapter_id", table_name="chapter_briefs")
    op.drop_table("chapter_briefs")
    op.drop_index("ix_ghostwriter_workspaces_book_id", table_name="ghostwriter_workspaces")
    op.drop_table("ghostwriter_workspaces")
