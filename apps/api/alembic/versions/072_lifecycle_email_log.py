"""lifecycle email log

The seven-message lifecycle ladder needs its own ledger: one row per user per
step, unique on (user_id, step) is the guarantee that a customer never receives
the same message twice even if the sweep is retried or restarted.

Additive only: a new table, nothing existing changes.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "072"
down_revision = "071"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lifecycle_email_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step", sa.String(40), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "step", name="uq_lifecycle_email_user_step"),
    )
    op.create_index("ix_lifecycle_email_log_user_id", "lifecycle_email_log", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_lifecycle_email_log_user_id", table_name="lifecycle_email_log")
    op.drop_table("lifecycle_email_log")
