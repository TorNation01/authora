"""Add project template system.

Revision ID: 023
Revises: 022
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "023"
down_revision: Union[str, None] = "022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("who_it_is_for", sa.Text, nullable=True),
        sa.Column("expected_outcome", sa.Text, nullable=True),
        sa.Column("suggested_workflow", sa.Text, nullable=True),
        sa.Column("book_type", sa.String(50), nullable=True),
        sa.Column("genre", sa.String(255), nullable=True),
        sa.Column("structure_framework", sa.String(100), nullable=True),
        sa.Column("default_structure", postgresql.JSONB, nullable=True),
        sa.Column("default_milestones", postgresql.JSONB, nullable=True),
        sa.Column("default_planning_prompts", postgresql.JSONB, nullable=True),
        sa.Column("default_accountability", postgresql.JSONB, nullable=True),
        sa.Column("ai_prompts", postgresql.JSONB, nullable=True),
        sa.Column("export_recommendations", postgresql.JSONB, nullable=True),
        sa.Column("setup_questions", postgresql.JSONB, nullable=True),
        sa.Column("chapter_skeletons", postgresql.JSONB, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_disabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["project_templates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_templates_slug", "project_templates", ["slug"], unique=True)
    op.create_index("ix_project_templates_category", "project_templates", ["category"])
    op.create_index("ix_project_templates_parent_id", "project_templates", ["parent_id"])
    op.create_index("ix_project_templates_sort", "project_templates", ["sort_order", "category"])

    op.add_column(
        "projects",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_projects_template",
        "projects",
        "project_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "books",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_books_template",
        "books",
        "project_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_books_template", "books", type_="foreignkey")
    op.drop_column("books", "template_id")
    op.drop_constraint("fk_projects_template", "projects", type_="foreignkey")
    op.drop_column("projects", "template_id")
    op.drop_index("ix_project_templates_sort", table_name="project_templates")
    op.drop_index("ix_project_templates_parent_id", table_name="project_templates")
    op.drop_index("ix_project_templates_category", table_name="project_templates")
    op.drop_index("ix_project_templates_slug", table_name="project_templates")
    op.drop_table("project_templates")
