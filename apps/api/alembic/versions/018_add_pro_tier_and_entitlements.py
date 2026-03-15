"""Add Pro tier, storage/ghostwriter limits, Stripe hooks placeholder.

Revision ID: 018
Revises: 017
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Pro plan (between free and premium for future use)
    op.execute("""
        INSERT INTO plans (id, slug, name, limits, features, sort_order) VALUES
        ('00000000-0000-0000-0000-000000000003'::uuid, 'pro', 'Pro',
         '{"projects": 10, "books": 50, "ai_actions_per_month": 200, "exports_per_month": 25,
           "export_formats": ["docx", "pdf", "epub", "txt"],
           "storage_mb": 500, "ghostwriter_sessions_per_month": 10}'::jsonb,
         '["planning", "editor", "notes", "accountability", "gamification", "ai", "export_pdf", "export_epub", "publishing_prep"]'::jsonb,
         2)
        ON CONFLICT (slug) DO NOTHING
    """)

    # Update free plan: add storage_mb, ghostwriter_sessions_per_month (0 = disabled)
    op.execute("""
        UPDATE plans SET limits = limits || '{"storage_mb": 50, "ghostwriter_sessions_per_month": 0}'::jsonb
        WHERE slug = 'free'
    """)

    # Update premium: add storage_mb, ghostwriter_sessions_per_month
    op.execute("""
        UPDATE plans SET limits = limits || '{"storage_mb": 2048, "ghostwriter_sessions_per_month": 50}'::jsonb
        WHERE slug = 'premium'
    """)

    # Pro plan: ghostwriter feature (optional - Pro has limited ghostwriter)
    op.execute("""
        UPDATE plans SET features = features || '["ghostwriter"]'::jsonb
        WHERE slug = 'pro'
    """)


def downgrade() -> None:
    op.execute("DELETE FROM plans WHERE slug = 'pro'")
    op.execute("""
        UPDATE plans SET limits = limits - 'storage_mb' - 'ghostwriter_sessions_per_month'
        WHERE slug IN ('free', 'premium')
    """)
