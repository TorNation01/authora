"""Character profiles: the missing fields + one-way, per-book relationships.

Additive only:
  * characters gains gender, profession, need, flaws, skills_limitations,
    values_boundaries, distinctive_behaviour, portrait_url, portrait_source,
    portrait_updated_at
  * new table character_relationships - how one character sees another in a
    given book, one-way by design, optionally starting at a chapter

Revision ID: 061
Revises: 060
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '061'
down_revision: Union[str, None] = '060'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for column in (
        sa.Column('gender', sa.String(60), nullable=True),
        sa.Column('profession', sa.String(200), nullable=True),
        sa.Column('need', sa.Text(), nullable=True),
        sa.Column('flaws', sa.Text(), nullable=True),
        sa.Column('skills_limitations', sa.Text(), nullable=True),
        sa.Column('values_boundaries', sa.Text(), nullable=True),
        sa.Column('distinctive_behaviour', sa.Text(), nullable=True),
        sa.Column('portrait_url', sa.Text(), nullable=True),
        sa.Column('portrait_source', sa.String(20), nullable=True),
        sa.Column('portrait_updated_at', sa.DateTime(timezone=True), nullable=True),
    ):
        op.add_column('characters', column)

    op.create_table(
        'character_bonds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('from_chapter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_chapter_id'], ['chapters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'book_id', 'from_character_id', 'to_character_id',
            name='uq_character_bonds_triple',
        ),
    )
    op.create_index('ix_character_bonds_book_id', 'character_bonds', ['book_id'])
    op.create_index(
        'ix_character_bonds_from', 'character_bonds', ['from_character_id']
    )


def downgrade() -> None:
    op.drop_index('ix_character_bonds_from', table_name='character_bonds')
    op.drop_index('ix_character_bonds_book_id', table_name='character_bonds')
    op.drop_table('character_bonds')
    for name in (
        'portrait_updated_at', 'portrait_source', 'portrait_url', 'distinctive_behaviour',
        'values_boundaries', 'skills_limitations', 'flaws', 'need', 'profession', 'gender',
    ):
        op.drop_column('characters', name)
