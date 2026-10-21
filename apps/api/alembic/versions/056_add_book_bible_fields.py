"""Book Bible fields: overview, character sheets, relationship intensity, character arcs, timeline anchors.

Additive only: every new column is nullable or carries a server default, so older
application code writing to these tables keeps working unchanged.

Revision ID: 056
Revises: 055
Create Date: 2026-10-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '056'
down_revision: Union[str, None] = '055'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Fiction workspace: the book-level bible header ---
    op.add_column('fiction_workspaces', sa.Column('logline', sa.Text(), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('subgenre', sa.String(length=255), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('audience', sa.String(length=255), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('pov', sa.String(length=100), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('tense', sa.String(length=50), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('target_word_count', sa.Integer(), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('comparable_titles', postgresql.JSONB(), nullable=True))
    op.add_column('fiction_workspaces', sa.Column('central_question', sa.Text(), nullable=True))

    # --- Fiction characters: full sheet ---
    op.add_column('fiction_characters', sa.Column('age', sa.String(length=100), nullable=True))
    op.add_column('fiction_characters', sa.Column('appearance', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('voice', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('need', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('wound', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('secret', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('arc_summary', sa.Text(), nullable=True))
    op.add_column('fiction_characters', sa.Column('first_appearance', sa.String(length=255), nullable=True))
    op.add_column('fiction_characters', sa.Column(
        'status', sa.String(length=50), nullable=False, server_default=sa.text("'active'")
    ))

    # --- Relationships: intensity 1-5 ---
    op.add_column('character_relationships', sa.Column(
        'intensity', sa.Integer(), nullable=False, server_default=sa.text('3')
    ))

    # --- Plot arcs: optional owning character ---
    op.add_column('plot_arcs', sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_plot_arcs_character_id_fiction_characters',
        'plot_arcs',
        'fiction_characters',
        ['character_id'],
        ['id'],
        ondelete='SET NULL',
    )

    # --- Timeline events: chapter anchor + present characters ---
    op.add_column('vault_timeline_events', sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_vault_timeline_events_chapter_id_chapters',
        'vault_timeline_events',
        'chapters',
        ['chapter_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.add_column('vault_timeline_events', sa.Column(
        'character_ids', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")
    ))


def downgrade() -> None:
    op.drop_column('vault_timeline_events', 'character_ids')
    op.drop_constraint('fk_vault_timeline_events_chapter_id_chapters', 'vault_timeline_events', type_='foreignkey')
    op.drop_column('vault_timeline_events', 'chapter_id')

    op.drop_constraint('fk_plot_arcs_character_id_fiction_characters', 'plot_arcs', type_='foreignkey')
    op.drop_column('plot_arcs', 'character_id')

    op.drop_column('character_relationships', 'intensity')

    for col in ('status', 'first_appearance', 'arc_summary', 'secret', 'wound', 'need', 'voice', 'appearance', 'age'):
        op.drop_column('fiction_characters', col)

    for col in ('central_question', 'comparable_titles', 'target_word_count', 'tense', 'pov', 'audience', 'subgenre', 'logline'):
        op.drop_column('fiction_workspaces', col)
