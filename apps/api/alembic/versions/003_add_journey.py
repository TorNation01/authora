"""Add journey tables

Revision ID: 003
Revises: 002
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_journeys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("book_type", sa.String(50), nullable=False),
        sa.Column("writing_mode", sa.String(50), nullable=False),
        sa.Column("writing_goals", sa.Text(), nullable=True),
        sa.Column("target_timeline", sa.String(100), nullable=True),
        sa.Column("writing_schedule", sa.String(100), nullable=True),
        sa.Column("accountability_style", sa.String(100), nullable=True),
        sa.Column("ai_comfort_level", sa.String(50), nullable=True),
        sa.Column("genre_topic", sa.String(255), nullable=True),
        sa.Column("roadmap", postgresql.JSONB(), nullable=True),
        sa.Column("current_phase", sa.String(50), nullable=False, server_default="idea"),
        sa.Column("phase_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_journeys_user_id", "user_journeys", ["user_id"], unique=True)

    op.create_table(
        "journey_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journey_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phase", sa.String(50), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("task_type", sa.String(50), nullable=False, server_default="checklist"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["journey_id"], ["user_journeys.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_journey_tasks_journey_phase", "journey_tasks", ["journey_id", "phase"])


def downgrade() -> None:
    op.drop_table("journey_tasks")
    op.drop_table("user_journeys")
