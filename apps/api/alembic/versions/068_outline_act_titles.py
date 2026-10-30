"""Author-titleable, unlimited outline acts

Revision ID: 068
Revises: 067
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "068"
down_revision: Union[str, None] = "067"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("outline_act_sheets", sa.Column("title", sa.String(length=120), nullable=True))
    op.add_column("outline_act_sheets", sa.Column("position", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("outline_act_sheets", "position")
    op.drop_column("outline_act_sheets", "title")
