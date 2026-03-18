"""Add creator profiles for template economy.

Revision ID: 045
Revises: 044
Create Date: 2025-03-18

Creator application, approval, dashboard access.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "045"
down_revision: Union[str, None] = "044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "creator_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("application_note", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_profiles_user_id", "creator_profiles", ["user_id"], unique=True)
    op.create_index("ix_creator_profiles_status", "creator_profiles", ["status"])

    op.add_column(
        "template_submissions",
        sa.Column("category", sa.String(50), nullable=True),
    )
    op.add_column(
        "template_submissions",
        sa.Column("price_cents", sa.Integer, nullable=True),
    )
    op.add_column(
        "template_submissions",
        sa.Column("approved_template_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_template_submissions_approved_template",
        "template_submissions",
        "project_templates",
        ["approved_template_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_template_submissions_approved_template", "template_submissions", type_="foreignkey")
    op.drop_column("template_submissions", "approved_template_id")
    op.drop_column("template_submissions", "price_cents")
    op.drop_column("template_submissions", "category")

    op.drop_index("ix_creator_profiles_status", table_name="creator_profiles")
    op.drop_index("ix_creator_profiles_user_id", table_name="creator_profiles")
    op.drop_table("creator_profiles")
