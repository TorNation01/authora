"""Add RAG content_embeddings and indexing jobs.

Revision ID: 021
Revises: 020
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "021"
down_revision: Union[str, None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("""
        CREATE TABLE content_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            source_type VARCHAR(50) NOT NULL,
            source_id UUID NOT NULL,
            book_id UUID REFERENCES books(id) ON DELETE CASCADE,
            chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL DEFAULT 0,
            content_text TEXT NOT NULL,
            metadata JSONB NOT NULL DEFAULT '{}',
            embedding_model VARCHAR(100),
            embedding vector(768),
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.create_index("ix_content_embeddings_project_id", "content_embeddings", ["project_id"])
    op.create_index("ix_content_embeddings_source", "content_embeddings", ["source_type", "source_id"])
    op.create_index("ix_content_embeddings_book_id", "content_embeddings", ["book_id"])
    op.execute(
        "CREATE INDEX ix_content_embeddings_vector ON content_embeddings "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1)"
    )

    op.create_table(
        "indexing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indexing_jobs_project_id", "indexing_jobs", ["project_id"])
    op.create_index("ix_indexing_jobs_status", "indexing_jobs", ["status"])


def downgrade() -> None:
    op.drop_table("indexing_jobs")
    op.drop_table("content_embeddings")
    op.execute("DROP EXTENSION IF EXISTS vector")
