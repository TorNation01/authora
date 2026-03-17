"""Add Story Density Engine tables.

Revision ID: 034
Revises: 033
Create Date: 2025-03-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "034"
down_revision: Union[str, None] = "033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "density_scans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("scan_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("chapter_count", sa.Integer(), nullable=True),
        sa.Column("issue_count", sa.Integer(), nullable=True),
        sa.Column("manuscript_density_score", sa.Float(), nullable=True),
        sa.Column("density_map_snapshot", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("triggered_by", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_density_scans_project_id", "density_scans", ["project_id"])
    op.create_index("ix_density_scans_book_id", "density_scans", ["book_id"])
    op.create_index("ix_density_scans_status", "density_scans", ["status"])
    op.create_index("ix_density_scans_started_at", "density_scans", ["started_at"])

    op.create_table(
        "density_issues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=True),
        sa.Column("issue_type", sa.String(80), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("action_category", sa.String(30), nullable=False, server_default="trim"),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_hint", sa.String(500), nullable=True),
        sa.Column("related_chapter_ids", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("fix_suggestions", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("marked_intentional_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["density_scans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_density_issues_scan_id", "density_issues", ["scan_id"])
    op.create_index("ix_density_issues_project_id", "density_issues", ["project_id"])
    op.create_index("ix_density_issues_book_id", "density_issues", ["book_id"])
    op.create_index("ix_density_issues_chapter_id", "density_issues", ["chapter_id"])
    op.create_index("ix_density_issues_status", "density_issues", ["status"])
    op.create_index("ix_density_issues_severity", "density_issues", ["severity"])
    op.create_index("ix_density_issues_category", "density_issues", ["category"])
    op.create_index("ix_density_issues_action_category", "density_issues", ["action_category"])


def downgrade() -> None:
    op.drop_table("density_issues")
    op.drop_table("density_scans")
