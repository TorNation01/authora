"""Add knowledge_mode and knowledge_modules to projects.

Revision ID: 032
Revises: 031
Create Date: 2025-03-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "032"
down_revision: Union[str, None] = "031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("knowledge_mode", sa.String(20), nullable=False, server_default="fiction"),
    )
    op.add_column(
        "projects",
        sa.Column("knowledge_modules", sa.dialects.postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("projects", "knowledge_modules")
    op.drop_column("projects", "knowledge_mode")
