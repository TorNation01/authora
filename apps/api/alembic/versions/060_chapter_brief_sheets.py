"""Chapter brief sheets - the 13-section brief for a single chapter.

Additive only:
  * chapter_brief_sheets - one structured brief per chapter

The existing ghostwriter `chapter_briefs` table is untouched.

Revision ID: 060
Revises: 059
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '060'
down_revision: Union[str, None] = '059'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chapter_brief_sheets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column('section_status', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chapter_id', name='uq_chapter_brief_sheets_chapter_id'),
    )
    op.create_index('ix_chapter_brief_sheets_book_id', 'chapter_brief_sheets', ['book_id'])
    op.create_index('ix_chapter_brief_sheets_chapter_id', 'chapter_brief_sheets', ['chapter_id'])


def downgrade() -> None:
    op.drop_index('ix_chapter_brief_sheets_chapter_id', table_name='chapter_brief_sheets')
    op.drop_index('ix_chapter_brief_sheets_book_id', table_name='chapter_brief_sheets')
    op.drop_table('chapter_brief_sheets')
