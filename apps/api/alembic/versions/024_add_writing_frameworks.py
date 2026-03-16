"""Add writing framework engine.

Revision ID: 024
Revises: 023
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "024"
down_revision: Union[str, None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "writing_frameworks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("book_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ideal_use_cases", sa.Text, nullable=True),
        sa.Column("ideal_genres", postgresql.JSONB, nullable=True),
        sa.Column("planning_stages", postgresql.JSONB, nullable=True),
        sa.Column("beat_stages", postgresql.JSONB, nullable=True),
        sa.Column("chapter_structure", postgresql.JSONB, nullable=True),
        sa.Column("manuscript_scaffolding", postgresql.JSONB, nullable=True),
        sa.Column("chapter_skeletons", postgresql.JSONB, nullable=True),
        sa.Column("milestone_logic", postgresql.JSONB, nullable=True),
        sa.Column("accountability_mapping", postgresql.JSONB, nullable=True),
        sa.Column("revision_checklist", postgresql.JSONB, nullable=True),
        sa.Column("ai_prompt_presets", postgresql.JSONB, nullable=True),
        sa.Column("recommendation_rules", postgresql.JSONB, nullable=True),
        sa.Column("scene_prompts", postgresql.JSONB, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_disabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_writing_frameworks_slug", "writing_frameworks", ["slug"], unique=True)
    op.create_index("ix_writing_frameworks_book_type", "writing_frameworks", ["book_type"])
    op.create_index("ix_writing_frameworks_sort", "writing_frameworks", ["sort_order", "book_type"])

    op.add_column(
        "books",
        sa.Column("framework_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_books_framework",
        "books",
        "writing_frameworks",
        ["framework_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_books_framework", "books", type_="foreignkey")
    op.drop_column("books", "framework_id")
    op.drop_index("ix_writing_frameworks_sort", table_name="writing_frameworks")
    op.drop_index("ix_writing_frameworks_book_type", table_name="writing_frameworks")
    op.drop_index("ix_writing_frameworks_slug", table_name="writing_frameworks")
    op.drop_table("writing_frameworks")
