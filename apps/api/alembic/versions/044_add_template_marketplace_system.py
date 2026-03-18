"""Add template marketplace system: ratings, creator submissions, revenue sharing.

Revision ID: 044
Revises: 043
Create Date: 2025-03-18

Future-ready: template ratings, creator submissions, revenue sharing.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "044"
down_revision: Union[str, None] = "043"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Template ratings (optional future) ---
    op.create_table(
        "template_ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("review", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["template_id"], ["project_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="template_ratings_rating_range"),
    )
    op.create_index("ix_template_ratings_template_id", "template_ratings", ["template_id"])
    op.create_index("ix_template_ratings_user_id", "template_ratings", ["user_id"])
    op.create_unique_constraint(
        "uq_template_ratings_user_template",
        "template_ratings",
        ["user_id", "template_id"],
    )

    # --- Creator submissions (future) ---
    op.create_table(
        "template_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("rejected_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_template_submissions_creator_id", "template_submissions", ["creator_id"])
    op.create_index("ix_template_submissions_status", "template_submissions", ["status"])

    # --- Revenue sharing on template_packs ---
    op.add_column(
        "template_packs",
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "template_packs",
        sa.Column("revenue_share_pct", sa.Numeric(5, 2), nullable=True),
    )
    op.create_foreign_key(
        "fk_template_packs_creator",
        "template_packs",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # --- Visibility control on template_packs ---
    op.add_column(
        "template_packs",
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_constraint("fk_template_packs_creator", "template_packs", type_="foreignkey")
    op.drop_column("template_packs", "is_featured")
    op.drop_column("template_packs", "revenue_share_pct")
    op.drop_column("template_packs", "creator_id")

    op.drop_index("ix_template_submissions_status", table_name="template_submissions")
    op.drop_index("ix_template_submissions_creator_id", table_name="template_submissions")
    op.drop_table("template_submissions")

    op.drop_constraint("uq_template_ratings_user_template", "template_ratings", type_="unique")
    op.drop_index("ix_template_ratings_user_id", table_name="template_ratings")
    op.drop_index("ix_template_ratings_template_id", table_name="template_ratings")
    op.drop_table("template_ratings")
