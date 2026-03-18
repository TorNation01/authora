"""Add premium template system: access levels, packs, purchases.

Revision ID: 043
Revises: 042
Create Date: 2025-03-15

Template access: free, pro, studio, premium_pack.
Premium packs: one-time purchase via Stripe.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "043"
down_revision: Union[str, None] = "042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Add access_level to project_templates ---
    op.add_column(
        "project_templates",
        sa.Column("access_level", sa.String(20), nullable=False, server_default="free"),
    )
    op.add_column(
        "project_templates",
        sa.Column("premium_pack_slug", sa.String(100), nullable=True),
    )
    op.create_index("ix_project_templates_access_level", "project_templates", ["access_level"])
    op.create_index("ix_project_templates_premium_pack_slug", "project_templates", ["premium_pack_slug"])

    # --- Template packs (bundles for one-time purchase) ---
    op.create_table(
        "template_packs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("price_cents", sa.Integer, nullable=False),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
        sa.Column("template_slugs", postgresql.ARRAY(sa.String(100)), nullable=False, server_default="{}"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_template_packs_slug", "template_packs", ["slug"], unique=True)

    # --- Template pack purchases (user bought a pack) ---
    op.create_table(
        "template_pack_purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pack_slug", sa.String(100), nullable=False),
        sa.Column("stripe_session_id", sa.String(255), nullable=True),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_template_pack_purchases_user_id", "template_pack_purchases", ["user_id"])
    op.create_index("ix_template_pack_purchases_user_pack", "template_pack_purchases", ["user_id", "pack_slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_template_pack_purchases_user_pack", table_name="template_pack_purchases")
    op.drop_index("ix_template_pack_purchases_user_id", table_name="template_pack_purchases")
    op.drop_table("template_pack_purchases")

    op.drop_index("ix_template_packs_slug", table_name="template_packs")
    op.drop_table("template_packs")

    op.drop_index("ix_project_templates_premium_pack_slug", table_name="project_templates")
    op.drop_index("ix_project_templates_access_level", table_name="project_templates")
    op.drop_column("project_templates", "premium_pack_slug")
    op.drop_column("project_templates", "access_level")
