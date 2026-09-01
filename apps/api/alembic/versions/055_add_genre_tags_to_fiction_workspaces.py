"""Add genre_tags to fiction_workspaces.

Revision ID: 055
Revises: 054
Create Date: 2026-08-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '055'
down_revision: Union[str, None] = '054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('fiction_workspaces', sa.Column(
        'genre_tags',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb")
    ))


def downgrade() -> None:
    op.drop_column('fiction_workspaces', 'genre_tags')
