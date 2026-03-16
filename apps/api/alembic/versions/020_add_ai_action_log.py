"""Add ai_action_log for AI usage tracking.

Revision ID: 020
Revises: 019
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_action_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_id", sa.String(100), nullable=False),
        sa.Column("mode", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_action_log_user_id", "ai_action_log", ["user_id"])
    op.create_index("ix_ai_action_log_book_id", "ai_action_log", ["book_id"])
    op.create_index("ix_ai_action_log_created_at", "ai_action_log", ["created_at"])

    # Add provider/model to ai_suggestions for revision tracking
    op.add_column("ai_suggestions", sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("ai_suggestions", sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("ai_suggestions", sa.Column("provider", sa.String(50), nullable=True))
    op.add_column("ai_suggestions", sa.Column("model", sa.String(100), nullable=True))
    op.add_column("ai_suggestions", sa.Column("input_tokens", sa.Integer(), nullable=True))
    op.add_column("ai_suggestions", sa.Column("output_tokens", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_ai_suggestions_project_id", "ai_suggestions", "projects", ["project_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_ai_suggestions_book_id", "ai_suggestions", "books", ["book_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_ai_suggestions_book_id", "ai_suggestions", type_="foreignkey")
    op.drop_constraint("fk_ai_suggestions_project_id", "ai_suggestions", type_="foreignkey")
    op.drop_column("ai_suggestions", "output_tokens")
    op.drop_column("ai_suggestions", "input_tokens")
    op.drop_column("ai_suggestions", "model")
    op.drop_column("ai_suggestions", "provider")
    op.drop_column("ai_suggestions", "book_id")
    op.drop_column("ai_suggestions", "project_id")

    op.drop_index("ix_ai_action_log_created_at", table_name="ai_action_log")
    op.drop_index("ix_ai_action_log_book_id", table_name="ai_action_log")
    op.drop_index("ix_ai_action_log_user_id", table_name="ai_action_log")
    op.drop_table("ai_action_log")
