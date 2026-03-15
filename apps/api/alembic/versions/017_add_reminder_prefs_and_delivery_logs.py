"""Add reminder preferences and notification delivery logs.

Revision ID: 017
Revises: 016
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend accountability_settings with reminder preferences
    op.add_column(
        "accountability_settings",
        sa.Column("timezone", sa.String(64), nullable=True, server_default="UTC"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("quiet_hours_start", sa.String(5), nullable=True),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("quiet_hours_end", sa.String(5), nullable=True),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("email_reminders_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("reminder_cadence", sa.String(20), nullable=False, server_default="daily"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("reminder_types", postgresql.JSONB, nullable=True),
    )

    # Notification delivery logs for tracking and retry
    op.create_table(
        "notification_delivery_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(100), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notification_delivery_logs_user_id",
        "notification_delivery_logs",
        ["user_id"],
    )
    op.create_index(
        "ix_notification_delivery_logs_status_created",
        "notification_delivery_logs",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_notification_delivery_logs_status_created", table_name="notification_delivery_logs")
    op.drop_index("ix_notification_delivery_logs_user_id", table_name="notification_delivery_logs")
    op.drop_table("notification_delivery_logs")

    op.drop_column("accountability_settings", "reminder_types")
    op.drop_column("accountability_settings", "reminder_cadence")
    op.drop_column("accountability_settings", "email_reminders_enabled")
    op.drop_column("accountability_settings", "quiet_hours_end")
    op.drop_column("accountability_settings", "quiet_hours_start")
    op.drop_column("accountability_settings", "timezone")
