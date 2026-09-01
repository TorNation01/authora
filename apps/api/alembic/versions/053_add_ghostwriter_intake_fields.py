"""Add ghostwriter intake fields — word count, deadline, author background, sample text, content warnings, research notes

Revision ID: 053
Revises: 052
Create Date: 2026-08-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "053"
down_revision: Union[str, None] = "052"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for col in ("word_count_target", "deadline", "author_background", "sample_text", "content_warnings", "research_notes"):
        op.add_column("ghostwriter_workspaces", sa.Column(col, sa.Text(), nullable=True))


def downgrade() -> None:
    for col in ("research_notes", "content_warnings", "sample_text", "author_background", "deadline", "word_count_target"):
        op.drop_column("ghostwriter_workspaces", col)
