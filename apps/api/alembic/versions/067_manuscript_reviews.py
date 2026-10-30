"""manuscript reviews

Revision ID: 067
Revises: 066
Create Date: 2026-10-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "067"
down_revision = "066"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manuscript_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("counts", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("words_at_review", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chapters_at_review", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("model", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_manuscript_reviews_book_id", "manuscript_reviews", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_manuscript_reviews_book_id", table_name="manuscript_reviews")
    op.drop_table("manuscript_reviews")
