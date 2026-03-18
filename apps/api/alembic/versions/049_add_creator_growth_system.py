"""Add creator growth system: featured creators, template analytics.

Revision ID: 049
Revises: 048
Create Date: 2025-03-18

Featured creators, trending templates, top sellers, view tracking.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "049"
down_revision: Union[str, None] = "048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "creator_profiles",
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("creator_profiles", "is_featured")
