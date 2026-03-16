"""Add guidance modes to projects.

Revision ID: 026
Revises: 025
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "026"
down_revision: Union[str, None] = "025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "guidance_mode",
            sa.String(20),
            nullable=False,
            server_default="guided",
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "guidance_mode")
