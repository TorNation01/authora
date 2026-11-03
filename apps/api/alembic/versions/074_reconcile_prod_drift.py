"""reconcile production drift: plans lifetime window, chapters.summary, export index

These three changes exist in the production database (authora_v2, at 073) but in
no migration: they were applied by hand. A fresh ``alembic upgrade head``
therefore produces a schema that is missing them, and anything that selects
``plans.lifetime_available_from`` - which the ORM model does, so every
``/api/v1/billing/plans`` request does - dies with UndefinedColumnError on the
first query after a clean deploy.

Guarded with IF NOT EXISTS so it is a no-op on the production database where the
objects already exist, and a real change on a database built from migrations.

Revision ID: 074
Revises: 073
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "074"
down_revision: Union[str, None] = "073"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE plans ADD COLUMN IF NOT EXISTS lifetime_available_from "
        "timestamp with time zone"
    )
    op.execute(
        "ALTER TABLE plans ADD COLUMN IF NOT EXISTS lifetime_available_to "
        "timestamp with time zone"
    )
    op.execute("ALTER TABLE chapters ADD COLUMN IF NOT EXISTS summary text")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_export_jobs_user "
        "ON export_jobs USING btree (user_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_export_jobs_user")
    op.execute("ALTER TABLE chapters DROP COLUMN IF EXISTS summary")
    op.execute("ALTER TABLE plans DROP COLUMN IF EXISTS lifetime_available_to")
    op.execute("ALTER TABLE plans DROP COLUMN IF EXISTS lifetime_available_from")
