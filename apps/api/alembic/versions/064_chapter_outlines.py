"""Chapter outlines - chapter-by-chapter map.

Revision ID: 064
Revises: 063
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '064'
down_revision: Union[str, None] = '063'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chapter_outlines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('turning_point_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['turning_point_id'], ['outline_turning_points.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chapter_id'),
    )
    op.create_index('ix_chapter_outlines_book_id', 'chapter_outlines', ['book_id'])
    op.create_index('ix_chapter_outlines_chapter_id', 'chapter_outlines', ['chapter_id'])


def downgrade() -> None:
    op.drop_index('ix_chapter_outlines_chapter_id', table_name='chapter_outlines')
    op.drop_index('ix_chapter_outlines_book_id', table_name='chapter_outlines')
    op.drop_table('chapter_outlines')
