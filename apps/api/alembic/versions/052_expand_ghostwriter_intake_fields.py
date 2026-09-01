"""Expand ghostwriter intake fields — voice_tone to Text, unlimited character support

Revision ID: 052
Revises: 051
Create Date: 2026-07-31

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "052"
down_revision: Union[str, None] = "051"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # voice_tone: String(255) → Text (unlimited)
    op.alter_column(
        "ghostwriter_workspaces",
        "voice_tone",
        existing_type=sa.String(255),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "ghostwriter_workspaces",
        "voice_tone",
        existing_type=sa.Text(),
        type_=sa.String(255),
        existing_nullable=True,
    )
