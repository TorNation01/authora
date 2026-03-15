"""Add billing system: plans, subscriptions, usage_records, admin override.

Revision ID: 016
Revises: 015
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Plans table - tier definitions (free, premium)
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("limits", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("features", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plans_slug", "plans", ["slug"], unique=True)

    # Subscriptions - user's current plan (manual or Stripe)
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_stripe_subscription_id", "subscriptions", ["stripe_subscription_id"])

    # Usage records - metered usage per user per period (monthly)
    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("metric", sa.String(50), nullable=False),
        sa.Column("value", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_records_user_period_metric", "usage_records", ["user_id", "period", "metric"], unique=True)

    # Admin override - bypass limits (optional column on users)
    op.add_column("users", sa.Column("plan_override_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("users", sa.Column("billing_exempt", sa.Boolean, nullable=False, server_default="false"))
    op.create_foreign_key(
        "fk_users_plan_override",
        "users",
        "plans",
        ["plan_override_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Seed default plans
    op.execute("""
        INSERT INTO plans (id, slug, name, limits, features, sort_order) VALUES
        ('00000000-0000-0000-0000-000000000001'::uuid, 'free', 'Free',
         '{"projects": 1, "books": 3, "ai_actions_per_month": 20, "exports_per_month": 5, "export_formats": ["docx", "txt"]}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification"]'::jsonb,
         0),
        ('00000000-0000-0000-0000-000000000002'::uuid, 'premium', 'Premium',
         '{"projects": 999, "books": 999, "ai_actions_per_month": 500, "exports_per_month": 50, "export_formats": ["docx", "pdf", "epub", "txt"]}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "ghostwriter", "export_pdf", "export_epub", "publishing_prep"]'::jsonb,
         1);
    """)


def downgrade() -> None:
    op.drop_constraint("fk_users_plan_override", "users", type_="foreignkey")
    op.drop_column("users", "billing_exempt")
    op.drop_column("users", "plan_override_id")
    op.drop_index("ix_usage_records_user_period_metric", table_name="usage_records")
    op.drop_table("usage_records")
    op.drop_index("ix_subscriptions_stripe_subscription_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index("ix_plans_slug", table_name="plans")
    op.drop_table("plans")
