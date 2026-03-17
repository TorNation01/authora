"""Add project management: section_group, tags for chapters.

Revision ID: 036
Revises: 035
Create Date: 2026-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "036"
down_revision: Union[str, None] = "035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chapters", sa.Column("section_group", sa.String(255), nullable=True))
    op.add_column("chapters", sa.Column("tags", sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))


def downgrade() -> None:
    op.drop_column("chapters", "tags")
    op.drop_column("chapters", "section_group")
