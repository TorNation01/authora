"""Add template quality control: changes_requested status, change_request_reason.

Revision ID: 048
Revises: 047
Create Date: 2025-03-18

Template validation, request changes flow, resubmit.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "048"
down_revision: Union[str, None] = "047"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "template_submissions",
        sa.Column("change_request_reason", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("template_submissions", "change_request_reason")
