"""Add genre_tags and themes to books and ghostwriter_workspaces.

Revision ID: 054
Revises: 053
Create Date: 2026-08-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '054'
down_revision: Union[str, None] = '053'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add genre_tags and themes to books
    op.add_column('books', sa.Column(
        'genre_tags',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb")
    ))
    op.add_column('books', sa.Column(
        'themes',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb")
    ))

    # Add genre_tags and themes to ghostwriter_workspaces
    op.add_column('ghostwriter_workspaces', sa.Column(
        'genre_tags',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb")
    ))
    op.add_column('ghostwriter_workspaces', sa.Column(
        'themes',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb")
    ))


def downgrade() -> None:
    op.drop_column('ghostwriter_workspaces', 'themes')
    op.drop_column('ghostwriter_workspaces', 'genre_tags')
    op.drop_column('books', 'themes')
    op.drop_column('books', 'genre_tags')
