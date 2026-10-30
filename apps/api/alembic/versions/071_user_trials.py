"""signup trials

A free trial has to live on the account, not in a Stripe object, because a
trial starts at registration — before there is any customer, payment method or
subscription. Three nullable columns are enough: when the trial is running the
account resolves to the trial plan (Starter by default), and when it ends the
same account falls back to Free with no cleanup job to run.

Additive only: no existing rows change, and a null ``trial_ends_at`` means
"never trialled", which is what every pre-existing account is.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "071"
down_revision = "070"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("trial_plan_slug", sa.String(50), nullable=True))
    op.create_index("ix_users_trial_ends_at", "users", ["trial_ends_at"])


def downgrade() -> None:
    op.drop_index("ix_users_trial_ends_at", table_name="users")
    op.drop_column("users", "trial_plan_slug")
    op.drop_column("users", "trial_ends_at")
    op.drop_column("users", "trial_started_at")
