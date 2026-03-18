"""Add template purchases for creator template sales.

Revision ID: 046
Revises: 045
Create Date: 2025-03-18

Individual template purchases, Stripe checkout, revenue tracking.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "046"
down_revision: Union[str, None] = "045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "template_purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("stripe_session_id", sa.String(255), nullable=True),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["project_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_template_purchases_user_id", "template_purchases", ["user_id"])
    op.create_index("ix_template_purchases_template_id", "template_purchases", ["template_id"])
    op.create_unique_constraint(
        "uq_template_purchases_user_template",
        "template_purchases",
        ["user_id", "template_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_template_purchases_user_template", "template_purchases", type_="unique")
    op.drop_index("ix_template_purchases_template_id", table_name="template_purchases")
    op.drop_index("ix_template_purchases_user_id", table_name="template_purchases")
    op.drop_table("template_purchases")
