"""Book Bible, character library and acts.

Additive only:
  * book_bibles        - the 15-section bible, one row per book
  * characters         - project-level character library
  * book_characters    - which library characters appear in which book
  * acts               - unlimited, ordered acts per book
  * chapters.act_id    - nullable link, existing rows untouched

Revision ID: 059
Revises: 058
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '059'
down_revision: Union[str, None] = '058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'book_bibles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column('section_status', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_id', name='uq_book_bibles_book_id'),
    )

    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('origin_book_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('continuation_of', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='supporting'),
        sa.Column('archetype', sa.String(length=120), nullable=True),
        sa.Column('one_line', sa.Text(), nullable=True),
        sa.Column('age', sa.String(length=80), nullable=True),
        sa.Column('pronouns', sa.String(length=40), nullable=True),
        sa.Column('appearance', sa.Text(), nullable=True),
        sa.Column('voice', sa.Text(), nullable=True),
        sa.Column('personality', sa.Text(), nullable=True),
        sa.Column('goals', sa.Text(), nullable=True),
        sa.Column('fears', sa.Text(), nullable=True),
        sa.Column('motivations', sa.Text(), nullable=True),
        sa.Column('internal_conflict', sa.Text(), nullable=True),
        sa.Column('external_conflict', sa.Text(), nullable=True),
        sa.Column('backstory', sa.Text(), nullable=True),
        sa.Column('wound', sa.Text(), nullable=True),
        sa.Column('secret', sa.Text(), nullable=True),
        sa.Column('arc_summary', sa.Text(), nullable=True),
        sa.Column('quirks', sa.Text(), nullable=True),
        sa.Column('dialogue_patterns', sa.Text(), nullable=True),
        sa.Column('relationships_notes', sa.Text(), nullable=True),
        sa.Column('private_notes', sa.Text(), nullable=True),
        sa.Column('canon_status', sa.String(length=20), nullable=False, server_default='working'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('extras', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['origin_book_id'], ['books.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['continuation_of'], ['characters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_characters_project_id', 'characters', ['project_id'])
    op.create_index('ix_characters_name', 'characters', ['name'])

    op.create_table(
        'book_characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_in_book', sa.String(length=80), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_book_characters_book_id', 'book_characters', ['book_id'])
    op.create_index('ix_book_characters_character_id', 'book_characters', ['character_id'])

    op.create_table(
        'acts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('target_words', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_acts_book_id', 'acts', ['book_id'])

    op.add_column('chapters', sa.Column('act_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_chapters_act_id', 'chapters', 'acts', ['act_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_chapters_act_id', 'chapters', type_='foreignkey')
    op.drop_column('chapters', 'act_id')
    op.drop_index('ix_acts_book_id', table_name='acts')
    op.drop_table('acts')
    op.drop_index('ix_book_characters_character_id', table_name='book_characters')
    op.drop_index('ix_book_characters_book_id', table_name='book_characters')
    op.drop_table('book_characters')
    op.drop_index('ix_characters_name', table_name='characters')
    op.drop_index('ix_characters_project_id', table_name='characters')
    op.drop_table('characters')
    op.drop_table('book_bibles')
