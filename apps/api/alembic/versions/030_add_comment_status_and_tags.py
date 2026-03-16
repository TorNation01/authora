"""Add comment status and expand tag support.

Revision ID: 030
Revises: 029
Create Date: 2025-03-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "030"
down_revision: Union[str, None] = "029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "content_comments",
        sa.Column("status", sa.String(30), nullable=False, server_default="open"),
    )
    op.create_index("ix_content_comments_status", "content_comments", ["status"])
    op.create_index("ix_content_comments_comment_type", "content_comments", ["comment_type"])


def downgrade() -> None:
    op.drop_index("ix_content_comments_comment_type", table_name="content_comments")
    op.drop_index("ix_content_comments_status", table_name="content_comments")
    op.drop_column("content_comments", "status")
