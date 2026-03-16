"""Add revision pass system.

Revision ID: 027
Revises: 026
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "027"
down_revision: Union[str, None] = "026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "revision_passes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("pass_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_revision_passes_project_id", "revision_passes", ["project_id"])
    op.create_index("ix_revision_passes_book_id", "revision_passes", ["book_id"])

    op.create_table(
        "revision_pass_chapters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("revision_pass_id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["revision_pass_id"], ["revision_passes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_revision_pass_chapters_revision_pass_id", "revision_pass_chapters", ["revision_pass_id"])
    op.create_index("ix_revision_pass_chapters_chapter_id", "revision_pass_chapters", ["chapter_id"])

    op.create_table(
        "revision_checklist_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("revision_pass_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["revision_pass_id"], ["revision_passes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_revision_checklist_items_revision_pass_id", "revision_checklist_items", ["revision_pass_id"])

    op.add_column(
        "content_comments",
        sa.Column("revision_pass_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_content_comments_revision_pass_id",
        "content_comments",
        "revision_passes",
        ["revision_pass_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_content_comments_revision_pass_id", "content_comments", ["revision_pass_id"])


def downgrade() -> None:
    op.drop_index("ix_content_comments_revision_pass_id", table_name="content_comments")
    op.drop_constraint("fk_content_comments_revision_pass_id", "content_comments", type_="foreignkey")
    op.drop_column("content_comments", "revision_pass_id")

    op.drop_index("ix_revision_checklist_items_revision_pass_id", table_name="revision_checklist_items")
    op.drop_table("revision_checklist_items")

    op.drop_index("ix_revision_pass_chapters_chapter_id", table_name="revision_pass_chapters")
    op.drop_index("ix_revision_pass_chapters_revision_pass_id", table_name="revision_pass_chapters")
    op.drop_table("revision_pass_chapters")

    op.drop_index("ix_revision_passes_book_id", table_name="revision_passes")
    op.drop_index("ix_revision_passes_project_id", table_name="revision_passes")
    op.drop_table("revision_passes")
