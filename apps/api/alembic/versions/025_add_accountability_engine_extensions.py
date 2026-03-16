"""Add accountability engine extensions.

Revision ID: 025
Revises: 024
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "025"
down_revision: Union[str, None] = "024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AccountabilitySettings: accountability_level, streak_visible, gamification_enabled, encouragement_preset
    op.add_column(
        "accountability_settings",
        sa.Column("accountability_level", sa.String(20), nullable=True),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("streak_visible", sa.Boolean, nullable=False, server_default="true"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("gamification_enabled", sa.Boolean, nullable=False, server_default="true"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("encouragement_preset", sa.String(50), nullable=True),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("reminder_style", sa.String(30), nullable=True),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("no_reminder_mode", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("grace_days", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "accountability_settings",
        sa.Column("flexible_streak_mode", sa.Boolean, nullable=False, server_default="false"),
    )

    # Goals: project_id, target_type, target_value, is_paused, low_energy_mode, metadata
    op.add_column(
        "goals",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "goals",
        sa.Column("target_type", sa.String(50), nullable=True),
    )
    op.add_column(
        "goals",
        sa.Column("target_value", sa.Integer, nullable=True),
    )
    op.add_column(
        "goals",
        sa.Column("is_paused", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "goals",
        sa.Column("low_energy_mode", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "goals",
        sa.Column("extra_data", postgresql.JSONB, nullable=True),
    )
    op.create_foreign_key(
        "fk_goals_project",
        "goals",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Milestones: milestone_type, framework_stage, sort_order, metadata
    op.add_column(
        "milestones",
        sa.Column("milestone_type", sa.String(50), nullable=True),
    )
    op.add_column(
        "milestones",
        sa.Column("framework_stage", sa.String(100), nullable=True),
    )
    op.add_column(
        "milestones",
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "milestones",
        sa.Column("extra_data", postgresql.JSONB, nullable=True),
    )

    # UserStats: grace_days_used (for streak grace logic)
    op.add_column(
        "user_stats",
        sa.Column("grace_days_used", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("user_stats", "grace_days_used")
    op.drop_column("milestones", "metadata")
    op.drop_column("milestones", "sort_order")
    op.drop_column("milestones", "framework_stage")
    op.drop_column("milestones", "milestone_type")
    op.drop_constraint("fk_goals_project", "goals", type_="foreignkey")
    op.drop_column("goals", "extra_data")
    op.drop_column("goals", "low_energy_mode")
    op.drop_column("goals", "is_paused")
    op.drop_column("goals", "target_value")
    op.drop_column("goals", "target_type")
    op.drop_column("goals", "project_id")
    op.drop_column("accountability_settings", "flexible_streak_mode")
    op.drop_column("accountability_settings", "grace_days")
    op.drop_column("accountability_settings", "no_reminder_mode")
    op.drop_column("accountability_settings", "reminder_style")
    op.drop_column("accountability_settings", "encouragement_preset")
    op.drop_column("accountability_settings", "gamification_enabled")
    op.drop_column("accountability_settings", "streak_visible")
    op.drop_column("accountability_settings", "accountability_level")
