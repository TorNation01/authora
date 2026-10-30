"""Overall Outline - turning points.

Revision ID: 063
Revises: 062
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '063'
down_revision: Union[str, None] = '062'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'outline_turning_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('act_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('title', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['act_id'], ['acts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_outline_turning_points_book_id', 'outline_turning_points', ['book_id'])
    op.create_index('ix_outline_turning_points_act_id', 'outline_turning_points', ['act_id'])


def downgrade() -> None:
    op.drop_index('ix_outline_turning_points_act_id', table_name='outline_turning_points')
    op.drop_index('ix_outline_turning_points_book_id', table_name='outline_turning_points')
    op.drop_table('outline_turning_points')
