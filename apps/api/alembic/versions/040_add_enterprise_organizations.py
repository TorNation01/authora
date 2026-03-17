"""Add enterprise organizations, org members, tenant isolation, org branding, org billing.

Revision ID: 040
Revises: 039
Create Date: 2026-03-15

Multi-tenant architecture:
- organizations: separate orgs with custom branding
- org_members: admin, manager, user roles
- tenant_id on users, projects, subscriptions, audit_logs
- org_subscriptions: org-level billing, seat-based
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "040"
down_revision: Union[str, None] = "039"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Organizations ---
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column(
            "branding",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "onboarding_config",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("ix_organizations_domain", "organizations", ["domain"], unique=True, postgresql_where=sa.text("domain IS NOT NULL"))

    # --- Org members (roles: admin, manager, user) ---
    op.create_table(
        "org_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_org_members_org_id", "org_members", ["org_id"])
    op.create_index("ix_org_members_user_id", "org_members", ["user_id"])
    op.create_unique_constraint("uq_org_members_org_user", "org_members", ["org_id", "user_id"])

    # --- Org subscriptions (org-level billing, seat-based) ---
    op.create_table(
        "org_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("seat_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("billing_interval", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_org_subscriptions_org_id", "org_subscriptions", ["org_id"])

    # --- Plan bulk pricing (seat tiers for orgs) ---
    op.add_column("plans", sa.Column("price_per_seat_monthly_cents", sa.Integer(), nullable=True))
    op.add_column("plans", sa.Column("price_per_seat_yearly_cents", sa.Integer(), nullable=True))
    op.add_column("plans", sa.Column("bulk_seat_tiers", postgresql.JSONB, nullable=True))

    # --- Tenant ID on users ---
    op.add_column("users", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_users_tenant_id",
        "users",
        "organizations",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_tenant_email", "users", ["tenant_id", "email"])

    # --- Tenant ID on projects ---
    op.add_column("projects", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_projects_tenant_id",
        "projects",
        "organizations",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_projects_tenant_id", "projects", ["tenant_id"])

    # --- Tenant ID on subscriptions ---
    op.add_column("subscriptions", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_subscriptions_tenant_id",
        "subscriptions",
        "organizations",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_subscriptions_tenant_id", "subscriptions", ["tenant_id"])

    # --- Tenant ID on audit_logs ---
    op.add_column("audit_logs", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_audit_logs_tenant_id",
        "audit_logs",
        "organizations",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])

    # Default tenant for standalone mode (slug 'default' reserved)
    op.execute("""
        INSERT INTO organizations (id, name, slug, branding, onboarding_config)
        VALUES ('00000000-0000-0000-0000-000000000000'::uuid, 'Default', 'default', '{}', '{}')
        ON CONFLICT (slug) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_tenant_id", table_name="audit_logs")
    op.drop_constraint("fk_audit_logs_tenant_id", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "tenant_id")

    op.drop_index("ix_subscriptions_tenant_id", table_name="subscriptions")
    op.drop_constraint("fk_subscriptions_tenant_id", "subscriptions", type_="foreignkey")
    op.drop_column("subscriptions", "tenant_id")

    op.drop_index("ix_projects_tenant_id", table_name="projects")
    op.drop_constraint("fk_projects_tenant_id", "projects", type_="foreignkey")
    op.drop_column("projects", "tenant_id")

    op.drop_index("ix_users_tenant_email", table_name="users")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_constraint("fk_users_tenant_id", "users", type_="foreignkey")
    op.drop_column("users", "tenant_id")

    op.drop_column("plans", "bulk_seat_tiers")
    op.drop_column("plans", "price_per_seat_yearly_cents")
    op.drop_column("plans", "price_per_seat_monthly_cents")

    op.drop_index("ix_org_subscriptions_org_id", table_name="org_subscriptions")
    op.drop_table("org_subscriptions")

    op.drop_constraint("uq_org_members_org_user", "org_members", type_="unique")
    op.drop_index("ix_org_members_user_id", table_name="org_members")
    op.drop_index("ix_org_members_org_id", table_name="org_members")
    op.drop_table("org_members")

    op.drop_index("ix_organizations_domain", table_name="organizations")
    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")
