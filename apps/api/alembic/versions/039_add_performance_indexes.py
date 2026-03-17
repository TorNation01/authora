"""Add performance indexes for projects list and books list.

Revision ID: 039
Revises: 038
Create Date: 2026-03-15

Indexes for list_projects (user_id, updated_at) and list_books (project_id).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "039"
down_revision: Union[str, None] = "038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_index("ix_projects_updated_at", "projects", ["updated_at"])
    op.create_index("ix_books_project_id", "books", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_books_project_id", table_name="books")
    op.drop_index("ix_projects_updated_at", table_name="projects")
    op.drop_index("ix_projects_user_id", table_name="projects")
