"""Add growth system: share_links, referrals, growth_settings.

Revision ID: 041
Revises: 040
Create Date: 2026-03-15

Viral share, referral loop, content generation, admin growth controls.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "041"
down_revision: Union[str, None] = "040"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Share links (shareable progress, milestones, achievements) ---
    op.create_table(
        "share_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("share_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_share_links_slug", "share_links", ["slug"], unique=True)
    op.create_index("ix_share_links_user_id", "share_links", ["user_id"])
    op.create_index("ix_share_links_share_type", "share_links", ["share_type"])

    # --- Referrals (invite loop) ---
    op.create_table(
        "referrals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inviter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invitee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("referral_code", sa.String(32), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reward_granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["inviter_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invitee_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_referrals_inviter_id", "referrals", ["inviter_id"])
    op.create_index("ix_referrals_referral_code", "referrals", ["referral_code"], unique=True)
    op.create_index("ix_referrals_invitee_id", "referrals", ["invitee_id"])

    # --- User referral code ---
    op.add_column("users", sa.Column("referral_code", sa.String(32), nullable=True))
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)

    # --- Growth settings (admin: feature toggles, incentives, campaigns) ---
    op.create_table(
        "growth_settings",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("key"),
    )
    op.execute("""
        INSERT INTO growth_settings (key, value) VALUES
        ('features', '{"share_progress": true, "share_milestones": true, "share_achievements": true, "referral_enabled": true}'::jsonb),
        ('incentives', '{"referral_reward_days": 7, "referral_invitee_reward_days": 3}'::jsonb),
        ('campaigns', '{}'::jsonb)
        ON CONFLICT (key) DO NOTHING
    """)

    # --- SEO content definitions (programmatic pages) ---
    op.create_table(
        "seo_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("page_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("meta_description", sa.String(500), nullable=True),
        sa.Column("content", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("internal_links", postgresql.ARRAY(sa.String())),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_seo_pages_slug", "seo_pages", ["slug"], unique=True)
    op.create_index("ix_seo_pages_page_type", "seo_pages", ["page_type"])

    # Seed example SEO pages (writing guides, use-cases)
    op.execute("""
        INSERT INTO seo_pages (id, slug, page_type, title, meta_description, content, internal_links, sort_order) VALUES
        ('a0000000-0000-0000-0000-000000000001'::uuid, 'how-to-write-a-novel', 'guide',
         'How to Write a Novel: A Step-by-Step Guide', 'Learn how to write a novel from idea to finished draft. AUTHORA guides you through outlining, drafting, and revising.',
         '{"sections": [{"title": "Start with an idea", "body": "Every novel begins with a spark."}, {"title": "Outline your story", "body": "Structure helps you stay on track."}]}'::jsonb,
         ARRAY['/for-fiction-writers', '/features', '/pricing'], 0),
        ('a0000000-0000-0000-0000-000000000002'::uuid, 'how-to-write-nonfiction', 'guide',
         'How to Write a Nonfiction Book', 'Write your nonfiction book with AUTHORA. From concept to manuscript with AI-assisted structure and clarity.',
         '{"sections": [{"title": "Define your expertise", "body": "What do you know that others need?"}, {"title": "Structure your content", "body": "Organize chapters for maximum impact."}]}'::jsonb,
         ARRAY['/for-nonfiction-writers', '/features', '/pricing'], 1),
        ('a0000000-0000-0000-0000-000000000003'::uuid, 'ai-writing-assistant', 'feature',
         'AI Writing Assistant for Authors', 'AUTHORA''s AI helps you write faster: expand outlines, improve clarity, match your voice. You stay in control.',
         '{"features": ["Expand outlines", "Improve clarity", "Style matching", "Ghostwriter mode"]}'::jsonb,
         ARRAY['/features', '/pricing', '/story-integrity-engine'], 2)
        ON CONFLICT (slug) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_index("ix_seo_pages_page_type", table_name="seo_pages")
    op.drop_index("ix_seo_pages_slug", table_name="seo_pages")
    op.drop_table("seo_pages")

    op.drop_table("growth_settings")

    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_column("users", "referral_code")

    op.drop_index("ix_referrals_invitee_id", table_name="referrals")
    op.drop_index("ix_referrals_referral_code", table_name="referrals")
    op.drop_index("ix_referrals_inviter_id", table_name="referrals")
    op.drop_table("referrals")

    op.drop_index("ix_share_links_share_type", table_name="share_links")
    op.drop_index("ix_share_links_user_id", table_name="share_links")
    op.drop_index("ix_share_links_slug", table_name="share_links")
    op.drop_table("share_links")
