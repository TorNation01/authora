"""Publisher submissions: one row per manuscript pack sent to a publishing house.

Additive only. Nothing existing is altered; the table records what was sent, the
reference the house returned, and the last status the house reported.

Revision ID: 058
Revises: 057
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '058'
down_revision: Union[str, None] = '057'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'publisher_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('publisher_name', sa.String(length=255), nullable=False),
        sa.Column('publisher_url', sa.String(length=500), nullable=True),
        sa.Column('ref', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='received'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('files', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_publisher_submissions_book_id', 'publisher_submissions', ['book_id'])
    op.create_index('ix_publisher_submissions_ref', 'publisher_submissions', ['ref'])


def downgrade() -> None:
    op.drop_index('ix_publisher_submissions_ref', table_name='publisher_submissions')
    op.drop_index('ix_publisher_submissions_book_id', table_name='publisher_submissions')
    op.drop_table('publisher_submissions')
