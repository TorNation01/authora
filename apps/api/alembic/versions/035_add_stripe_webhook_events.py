"""Add stripe_webhook_events for idempotency.

Revision ID: 035
Revises: 034
Create Date: 2025-03-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "035"
down_revision: Union[str, None] = "034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stripe_event_id", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stripe_webhook_events_stripe_event_id",
        "stripe_webhook_events",
        ["stripe_event_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_stripe_webhook_events_stripe_event_id", table_name="stripe_webhook_events")
    op.drop_table("stripe_webhook_events")
