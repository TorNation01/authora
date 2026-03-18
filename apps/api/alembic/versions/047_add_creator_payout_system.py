"""Add creator payout system: earnings, payouts, Stripe Connect.

Revision ID: 047
Revises: 046
Create Date: 2025-03-18

Creator earnings from template sales, payout requests, admin approval.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "047"
down_revision: Union[str, None] = "046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "creator_profiles",
        sa.Column("stripe_connect_account_id", sa.String(255), nullable=True),
    )
    op.add_column(
        "creator_profiles",
        sa.Column("revenue_share_pct", sa.Numeric(5, 2), nullable=True),
    )

    op.create_table(
        "creator_payouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("stripe_payout_id", sa.String(255), nullable=True),
        sa.Column("payment_details", postgresql.JSONB, nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_payouts_creator_id", "creator_payouts", ["creator_id"])
    op.create_index("ix_creator_payouts_status", "creator_payouts", ["status"])

    op.create_table(
        "creator_earnings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_purchase_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payout_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_purchase_id"], ["template_purchases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_earnings_creator_id", "creator_earnings", ["creator_id"])
    op.create_index("ix_creator_earnings_status", "creator_earnings", ["status"])
    op.create_unique_constraint(
        "uq_creator_earnings_purchase",
        "creator_earnings",
        ["template_purchase_id"],
    )

    op.create_table(
        "creator_balance_adjustments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("admin_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_balance_adjustments_creator_id", "creator_balance_adjustments", ["creator_id"])


def downgrade() -> None:
    op.drop_index("ix_creator_balance_adjustments_creator_id", table_name="creator_balance_adjustments")
    op.drop_table("creator_balance_adjustments")

    op.drop_index("ix_creator_payouts_status", table_name="creator_payouts")
    op.drop_index("ix_creator_payouts_creator_id", table_name="creator_payouts")
    op.drop_table("creator_payouts")

    op.drop_constraint("uq_creator_earnings_purchase", "creator_earnings", type_="unique")
    op.drop_index("ix_creator_earnings_status", table_name="creator_earnings")
    op.drop_index("ix_creator_earnings_creator_id", table_name="creator_earnings")
    op.drop_table("creator_earnings")

    op.drop_column("creator_profiles", "revenue_share_pct")
    op.drop_column("creator_profiles", "stripe_connect_account_id")
