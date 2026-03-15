"""Add editing and polish engine tables

Revision ID: 010
Revises: 009
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Editorial analysis jobs (chapter or book scope)
    op.create_table(
        "editorial_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editorial_jobs_book_id", "editorial_jobs", ["book_id"])
    op.create_index("ix_editorial_jobs_status", "editorial_jobs", ["status"])

    # Editorial analysis results (per chapter)
    op.create_table(
        "editorial_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["editorial_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editorial_analyses_chapter_id", "editorial_analyses", ["chapter_id"])
    op.create_index("ix_editorial_analyses_type", "editorial_analyses", ["analysis_type"])

    # Inline suggestions (for user acceptance)
    op.create_table(
        "editorial_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("suggestion_type", sa.String(50), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=True),
        sa.Column("suggested_text", sa.Text(), nullable=True),
        sa.Column("position_start", sa.Integer(), nullable=True),
        sa.Column("position_end", sa.Integer(), nullable=True),
        sa.Column("suggestion_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["editorial_analyses.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editorial_suggestions_chapter_id", "editorial_suggestions", ["chapter_id"])
    op.create_index("ix_editorial_suggestions_status", "editorial_suggestions", ["status"])

    # Before/after comparison snapshots
    op.create_table(
        "editorial_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_before", postgresql.JSONB(), nullable=False),
        sa.Column("content_after", postgresql.JSONB(), nullable=True),
        sa.Column("snapshot_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editorial_snapshots_chapter_id", "editorial_snapshots", ["chapter_id"])


def downgrade() -> None:
    op.drop_index("ix_editorial_snapshots_chapter_id", table_name="editorial_snapshots")
    op.drop_table("editorial_snapshots")
    op.drop_index("ix_editorial_suggestions_status", table_name="editorial_suggestions")
    op.drop_index("ix_editorial_suggestions_chapter_id", table_name="editorial_suggestions")
    op.drop_table("editorial_suggestions")
    op.drop_index("ix_editorial_analyses_type", table_name="editorial_analyses")
    op.drop_index("ix_editorial_analyses_chapter_id", table_name="editorial_analyses")
    op.drop_table("editorial_analyses")
    op.drop_index("ix_editorial_jobs_status", table_name="editorial_jobs")
    op.drop_index("ix_editorial_jobs_book_id", table_name="editorial_jobs")
    op.drop_table("editorial_jobs")
