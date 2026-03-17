"""Add community tables: writing groups, feedback threads, profile visibility.

Revision ID: 038
Revises: 037
Create Date: 2026-03-15

Optional community features - fully opt-in, privacy-first.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "038"
down_revision: Union[str, None] = "037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Profile: optional public profile (privacy-first)
    op.add_column("profiles", sa.Column("profile_visibility", sa.String(20), nullable=False, server_default="private"))
    op.add_column("profiles", sa.Column("profile_slug", sa.String(100), nullable=True))
    op.create_index("ix_profiles_profile_slug", "profiles", ["profile_slug"], unique=True)

    # Writing groups
    op.create_table(
        "writing_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "writing_group_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["group_id"], ["writing_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_writing_group_members_group_id", "writing_group_members", ["group_id"])
    op.create_index("ix_writing_group_members_user_id", "writing_group_members", ["user_id"])

    op.create_table(
        "writing_group_invites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("invited_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["group_id"], ["writing_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_writing_group_invites_token", "writing_group_invites", ["token"], unique=True)

    # Feedback threads
    op.create_table(
        "feedback_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_threads_project_id", "feedback_threads", ["project_id"])

    op.create_table(
        "feedback_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["thread_id"], ["feedback_threads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_comments_thread_id", "feedback_comments", ["thread_id"])


def downgrade() -> None:
    op.drop_index("ix_feedback_comments_thread_id", table_name="feedback_comments")
    op.drop_table("feedback_comments")
    op.drop_index("ix_feedback_threads_project_id", table_name="feedback_threads")
    op.drop_table("feedback_threads")
    op.drop_index("ix_writing_group_invites_token", table_name="writing_group_invites")
    op.drop_table("writing_group_invites")
    op.drop_index("ix_writing_group_members_user_id", table_name="writing_group_members")
    op.drop_index("ix_writing_group_members_group_id", table_name="writing_group_members")
    op.drop_table("writing_group_members")
    op.drop_table("writing_groups")
    op.drop_index("ix_profiles_profile_slug", table_name="profiles")
    op.drop_column("profiles", "profile_slug")
    op.drop_column("profiles", "profile_visibility")
