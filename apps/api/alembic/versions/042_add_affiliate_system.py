"""Add affiliate system: profiles, clicks, conversions, commissions, payouts.

Revision ID: 042
Revises: 041
Create Date: 2026-03-15

Affiliate accounts, tracking, commissions, payouts, fraud prevention.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "042"
down_revision: Union[str, None] = "041"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Affiliate profiles (apply, approve, commission rates) ---
    op.create_table(
        "affiliate_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("commission_rate_pct", sa.Numeric(5, 2), nullable=False, server_default="20"),
        sa.Column("commission_recurring_pct", sa.Numeric(5, 2), nullable=True),
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
    op.create_index("ix_affiliate_profiles_user_id", "affiliate_profiles", ["user_id"], unique=True)
    op.create_index("ix_affiliate_profiles_code", "affiliate_profiles", ["code"], unique=True)
    op.create_index("ix_affiliate_profiles_status", "affiliate_profiles", ["status"])

    # --- Affiliate clicks (tracking) ---
    op.create_table(
        "affiliate_clicks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fingerprint_hash", sa.String(64), nullable=True),
        sa.Column("landing_path", sa.String(500), nullable=True),
        sa.Column("referrer", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["affiliate_id"], ["affiliate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_affiliate_clicks_affiliate_id", "affiliate_clicks", ["affiliate_id"])
    op.create_index("ix_affiliate_clicks_created_at", "affiliate_clicks", ["created_at"])

    # --- Affiliate conversions (signup + revenue) ---
    op.create_table(
        "affiliate_conversions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revenue_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("commission_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("commission_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("fraud_flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("fraud_reason", sa.String(255), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["affiliate_id"], ["affiliate_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_affiliate_conversions_affiliate_id", "affiliate_conversions", ["affiliate_id"])
    op.create_index("ix_affiliate_conversions_user_id", "affiliate_conversions", ["user_id"])
    op.create_index("ix_affiliate_conversions_affiliate_user", "affiliate_conversions", ["affiliate_id", "user_id"])

    # --- Affiliate attributions (user signup → attribution to affiliate) ---
    op.create_table(
        "affiliate_attributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attributed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["affiliate_id"], ["affiliate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_affiliate_attributions_user_id", "affiliate_attributions", ["user_id"], unique=True)
    op.create_index("ix_affiliate_attributions_affiliate_id", "affiliate_attributions", ["affiliate_id"])

    # --- Affiliate payout requests ---
    op.create_table(
        "affiliate_payouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("stripe_payout_id", sa.String(255), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("payment_details", postgresql.JSONB, nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["affiliate_id"], ["affiliate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_affiliate_payouts_affiliate_id", "affiliate_payouts", ["affiliate_id"])
    op.create_index("ix_affiliate_payouts_status", "affiliate_payouts", ["status"])

    # --- Affiliate settings (admin: default rates, rules) ---
    op.execute("""
        INSERT INTO growth_settings (key, value) VALUES
        ('affiliate', '{"enabled": true, "default_commission_pct": 20, "recurring_commission_pct": 10, "min_payout_cents": 5000, "cookie_days": 30}'::jsonb)
        ON CONFLICT (key) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM growth_settings WHERE key = 'affiliate'")

    op.drop_index("ix_affiliate_payouts_status", table_name="affiliate_payouts")
    op.drop_index("ix_affiliate_payouts_affiliate_id", table_name="affiliate_payouts")
    op.drop_table("affiliate_payouts")

    op.drop_index("ix_affiliate_attributions_affiliate_id", table_name="affiliate_attributions")
    op.drop_index("ix_affiliate_attributions_user_id", table_name="affiliate_attributions")
    op.drop_table("affiliate_attributions")

    op.drop_index("ix_affiliate_conversions_affiliate_user", table_name="affiliate_conversions")
    op.drop_index("ix_affiliate_conversions_user_id", table_name="affiliate_conversions")
    op.drop_index("ix_affiliate_conversions_affiliate_id", table_name="affiliate_conversions")
    op.drop_table("affiliate_conversions")

    op.drop_index("ix_affiliate_clicks_created_at", table_name="affiliate_clicks")
    op.drop_index("ix_affiliate_clicks_affiliate_id", table_name="affiliate_clicks")
    op.drop_table("affiliate_clicks")

    op.drop_index("ix_affiliate_profiles_status", table_name="affiliate_profiles")
    op.drop_index("ix_affiliate_profiles_code", table_name="affiliate_profiles")
    op.drop_index("ix_affiliate_profiles_user_id", table_name="affiliate_profiles")
    op.drop_table("affiliate_profiles")
