"""Full billing: plans pricing, entitlement grants, promo codes, audit log.

Revision ID: 022
Revises: 021
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "022"
down_revision: Union[str, None] = "021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Plan extensions: pricing and Stripe price IDs ---
    op.add_column("plans", sa.Column("price_monthly_cents", sa.Integer, nullable=True))
    op.add_column("plans", sa.Column("price_yearly_cents", sa.Integer, nullable=True))
    op.add_column("plans", sa.Column("price_lifetime_cents", sa.Integer, nullable=True))
    op.add_column("plans", sa.Column("stripe_price_id_monthly", sa.String(255), nullable=True))
    op.add_column("plans", sa.Column("stripe_price_id_yearly", sa.String(255), nullable=True))
    op.add_column("plans", sa.Column("stripe_price_id_lifetime", sa.String(255), nullable=True))

    # --- Subscription extensions ---
    op.add_column(
        "subscriptions",
        sa.Column("billing_interval", sa.String(20), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("grace_period_end", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("is_lifetime", sa.Boolean, nullable=False, server_default="false"),
    )
    op.execute("UPDATE subscriptions SET billing_interval = 'monthly' WHERE billing_interval IS NULL")

    # --- Entitlement grants (admin manual grants) ---
    op.create_table(
        "entitlement_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("reason_custom", sa.String(255), nullable=True),
        sa.Column("access_type", sa.String(20), nullable=False, server_default="free"),
        sa.Column("override_stripe", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("on_expiry", sa.String(30), nullable=False, server_default="revert_free"),
        sa.Column("internal_notes", sa.Text, nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["granted_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entitlement_grants_user_id", "entitlement_grants", ["user_id"])
    op.create_index("ix_entitlement_grants_expires_at", "entitlement_grants", ["expires_at"])
    op.create_index(
        "ix_entitlement_grants_active",
        "entitlement_grants",
        ["user_id", "revoked_at"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    # --- Promo codes (admin-controlled access codes) ---
    op.create_table(
        "promo_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("discount_type", sa.String(20), nullable=False, server_default="free"),
        sa.Column("discount_value", sa.Integer, nullable=True),
        sa.Column("duration_months", sa.Integer, nullable=True),
        sa.Column("duration_years", sa.Integer, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_uses", sa.Integer, nullable=True),
        sa.Column("use_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("internal_note", sa.Text, nullable=True),
        sa.Column("is_stripe_compatible", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("allowed_user_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promo_codes_code", "promo_codes", ["code"], unique=True)
    op.create_index("ix_promo_codes_plan_id", "promo_codes", ["plan_id"])

    # --- Promo code redemptions ---
    op.create_table(
        "promo_code_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("promo_code_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entitlement_grant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["promo_code_id"], ["promo_codes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entitlement_grant_id"], ["entitlement_grants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promo_code_redemptions_user_id", "promo_code_redemptions", ["user_id"])
    op.create_index("ix_promo_code_redemptions_promo_code_id", "promo_code_redemptions", ["promo_code_id"])

    # --- Entitlement audit log ---
    op.create_table(
        "entitlement_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("performed_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entitlement_audit_log_user_id", "entitlement_audit_log", ["user_id"])
    op.create_index("ix_entitlement_audit_log_action", "entitlement_audit_log", ["action"])
    op.create_index("ix_entitlement_audit_log_created_at", "entitlement_audit_log", ["created_at"])

    # --- Seed full plan tiers (Free, Starter, Pro, Studio, Founder Lifetime) ---
    # Migrate subscriptions from old premium/pro to new pro before deleting plans
    op.execute("""
        UPDATE subscriptions SET plan_id = '00000000-0000-0000-0000-000000000003'::uuid
        WHERE plan_id IN (SELECT id FROM plans WHERE slug IN ('premium', 'pro'))
    """)
    op.execute("DELETE FROM plans WHERE slug IN ('premium', 'pro')")

    op.execute("""
        UPDATE plans SET
            price_monthly_cents = 0,
            price_yearly_cents = 0,
            price_lifetime_cents = NULL,
            limits = '{"projects": 1, "books": 3, "ai_actions_per_month": 20, "exports_per_month": 5,
                "export_formats": ["docx", "txt"], "storage_mb": 50, "ghostwriter_sessions_per_month": 0}'::jsonb,
            features = '["planning", "editor", "notes", "accountability", "gamification"]'::jsonb
        WHERE slug = 'free'
    """)

    op.execute("""
        INSERT INTO plans (id, slug, name, limits, features, sort_order, price_monthly_cents, price_yearly_cents, price_lifetime_cents) VALUES
        ('00000000-0000-0000-0000-000000000002'::uuid, 'starter', 'Starter',
         '{"projects": 3, "books": 3, "ai_actions_per_month": 100, "exports_per_month": 20,
           "export_formats": ["docx", "pdf", "epub", "txt"], "storage_mb": 200, "ghostwriter_sessions_per_month": 0}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "export_pdf", "export_epub"]'::jsonb,
         1, 1200, 10800, NULL),
        ('00000000-0000-0000-0000-000000000003'::uuid, 'pro', 'Pro',
         '{"projects": 20, "books": 50, "ai_actions_per_month": 300, "exports_per_month": 50,
           "export_formats": ["docx", "pdf", "epub", "txt"], "storage_mb": 1024, "ghostwriter_sessions_per_month": 15}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "ghostwriter", "export_pdf", "export_epub", "publishing_prep", "finish_mode", "semantic_search"]'::jsonb,
         2, 2400, 21600, NULL),
        ('00000000-0000-0000-0000-000000000004'::uuid, 'studio', 'Studio',
         '{"projects": 999, "books": 999, "ai_actions_per_month": 1000, "exports_per_month": 100,
           "export_formats": ["docx", "pdf", "epub", "txt"], "storage_mb": 2048, "ghostwriter_sessions_per_month": 50}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "ghostwriter", "export_pdf", "export_epub", "publishing_prep", "finish_mode", "semantic_search", "premium_model_routing"]'::jsonb,
         3, 4900, 46800, NULL),
        ('00000000-0000-0000-0000-000000000005'::uuid, 'founder_lifetime', 'Founder Lifetime',
         '{"projects": 999, "books": 999, "ai_actions_per_month": 500, "exports_per_month": 50,
           "export_formats": ["docx", "pdf", "epub", "txt"], "storage_mb": 1024, "ghostwriter_sessions_per_month": 25}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "ghostwriter", "export_pdf", "export_epub", "publishing_prep", "finish_mode", "semantic_search"]'::jsonb,
         4, NULL, NULL, 34900)
    """)
    op.execute("UPDATE plans SET sort_order = 0 WHERE slug = 'free'")
    op.execute("UPDATE plans SET sort_order = 1 WHERE slug = 'starter'")
    op.execute("UPDATE plans SET sort_order = 2 WHERE slug = 'pro'")
    op.execute("UPDATE plans SET sort_order = 3 WHERE slug = 'studio'")
    op.execute("UPDATE plans SET sort_order = 4 WHERE slug = 'founder_lifetime'")


def downgrade() -> None:
    op.drop_index("ix_entitlement_audit_log_created_at", table_name="entitlement_audit_log")
    op.drop_index("ix_entitlement_audit_log_action", table_name="entitlement_audit_log")
    op.drop_index("ix_entitlement_audit_log_user_id", table_name="entitlement_audit_log")
    op.drop_table("entitlement_audit_log")

    op.drop_index("ix_promo_code_redemptions_promo_code_id", table_name="promo_code_redemptions")
    op.drop_index("ix_promo_code_redemptions_user_id", table_name="promo_code_redemptions")
    op.drop_table("promo_code_redemptions")

    op.drop_index("ix_promo_codes_plan_id", table_name="promo_codes")
    op.drop_index("ix_promo_codes_code", table_name="promo_codes")
    op.drop_table("promo_codes")

    op.drop_index("ix_entitlement_grants_active", table_name="entitlement_grants")
    op.drop_index("ix_entitlement_grants_expires_at", table_name="entitlement_grants")
    op.drop_index("ix_entitlement_grants_user_id", table_name="entitlement_grants")
    op.drop_table("entitlement_grants")

    op.drop_column("subscriptions", "is_lifetime")
    op.drop_column("subscriptions", "grace_period_end")
    op.drop_column("subscriptions", "billing_interval")

    op.drop_column("plans", "stripe_price_id_lifetime")
    op.drop_column("plans", "stripe_price_id_yearly")
    op.drop_column("plans", "stripe_price_id_monthly")
    op.drop_column("plans", "price_lifetime_cents")
    op.drop_column("plans", "price_yearly_cents")
    op.drop_column("plans", "price_monthly_cents")
