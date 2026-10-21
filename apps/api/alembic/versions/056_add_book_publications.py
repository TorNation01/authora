"""Add book_publications table (publishing metadata + release record).

Revision ID: 056
Revises: 055
Create Date: 2026-10-21

Stores the metadata an author needs to take a finished manuscript to market
(title page data, blurb, keywords, ISBN, imprint) and the record of the
release itself. Nothing here contacts a retailer or a distributor; it is the
author's own record of intent.
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
    op.create_table(
        'book_publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        # Metadata
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('subtitle', sa.String(length=500), nullable=True),
        sa.Column('author_name', sa.String(length=255), nullable=True),
        sa.Column('blurb', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(length=1000), nullable=True),
        sa.Column('keywords', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('categories', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('language', sa.String(length=10), nullable=False, server_default=sa.text("'en'")),
        sa.Column('isbn', sa.String(length=20), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('imprint', sa.String(length=255), nullable=False,
                  server_default=sa.text("'Anema House Publishing'")),
        # Front / back matter
        sa.Column('copyright_notice', sa.Text(), nullable=True),
        sa.Column('dedication', sa.Text(), nullable=True),
        sa.Column('front_matter', sa.Text(), nullable=True),
        sa.Column('acknowledgements', sa.Text(), nullable=True),
        sa.Column('author_bio', sa.Text(), nullable=True),
        sa.Column('back_matter', sa.Text(), nullable=True),
        sa.Column('include_imprint_page', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        # Release record (intent only - nothing is transmitted to retailers)
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('release_formats', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('release_imprint', sa.String(length=255), nullable=True),
        sa.Column('release_isbn', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('book_id', name='uq_book_publications_book_id'),
    )
    op.create_index('ix_book_publications_book_id', 'book_publications', ['book_id'])


def downgrade() -> None:
    op.drop_index('ix_book_publications_book_id', table_name='book_publications')
    op.drop_table('book_publications')
