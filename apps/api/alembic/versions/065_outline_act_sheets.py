"""outline act sheets

Revision ID: 065
Revises: 064
Create Date: 2026-10-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "065"
down_revision = "064"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outline_act_sheets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("act_key", sa.String(length=40), nullable=False),
        sa.Column("sections", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("book_id", "act_key", name="uq_outline_act_sheets_book_act"),
    )
    op.create_index("ix_outline_act_sheets_book_id", "outline_act_sheets", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_outline_act_sheets_book_id", table_name="outline_act_sheets")
    op.drop_table("outline_act_sheets")
