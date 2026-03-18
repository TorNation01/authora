"""Add reference, citation, bibliography, and Zotero integration system.

Revision ID: 050
Revises: 049
Create Date: 2025-03-15

Zotero connections, source sync, citation styles, in-editor citations,
source notes, project-linked references.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "050"
down_revision: Union[str, None] = "049"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Zotero connection per user (API key, library type, library ID)
    op.create_table(
        "zotero_connections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("library_type", sa.String(20), nullable=False),
        sa.Column("library_id", sa.String(50), nullable=False),
        sa.Column("api_key", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_version", sa.BigInteger(), nullable=True),
        sa.Column("sync_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("sync_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_zotero_connections_user_id", "zotero_connections", ["user_id"])

    # Citation styles (CSL) - built-in and custom
    op.create_table(
        "citation_styles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("csl_xml", sa.Text(), nullable=True),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_citation_styles_slug", "citation_styles", ["slug"], unique=True)

    # Project-level citation style preference
    op.create_table(
        "project_citation_styles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=True),
        sa.Column("citation_style_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["citation_style_id"], ["citation_styles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_citation_styles_project_id", "project_citation_styles", ["project_id"])
    op.create_index("ix_project_citation_styles_book_id", "project_citation_styles", ["book_id"])

    # Source notes / annotations on vault sources
    op.create_table(
        "source_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("note_type", sa.String(50), nullable=False, server_default="annotation"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_ref", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["vault_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_notes_source_id", "source_notes", ["source_id"])

    # In-editor citation markers (linked to source, stored in chapter content or separate table)
    op.create_table(
        "chapter_citations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("chapter_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("citation_key", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["vault_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_citations_chapter_id", "chapter_citations", ["chapter_id"])
    op.create_index("ix_chapter_citations_source_id", "chapter_citations", ["source_id"])

    # Add Zotero fields to vault_sources
    op.add_column("vault_sources", sa.Column("zotero_connection_id", sa.UUID(), nullable=True))
    op.add_column("vault_sources", sa.Column("zotero_item_key", sa.String(50), nullable=True))
    op.add_column("vault_sources", sa.Column("zotero_version", sa.BigInteger(), nullable=True))
    op.add_column("vault_sources", sa.Column("csl_json", sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column("vault_sources", sa.Column("used_in_manuscript", sa.Boolean(), nullable=False, server_default="false"))
    op.create_foreign_key(
        "fk_vault_sources_zotero_connection",
        "vault_sources",
        "zotero_connections",
        ["zotero_connection_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_vault_sources_zotero_item_key", "vault_sources", ["zotero_item_key"])

    # Link citation placeholders to sources when resolved
    op.add_column("citation_placeholders", sa.Column("source_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_citation_placeholders_source",
        "citation_placeholders",
        "vault_sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_citation_placeholders_source", "citation_placeholders", type_="foreignkey")
    op.drop_column("citation_placeholders", "source_id")

    op.drop_index("ix_vault_sources_zotero_item_key", "vault_sources")
    op.drop_constraint("fk_vault_sources_zotero_connection", "vault_sources", type_="foreignkey")
    op.drop_column("vault_sources", "used_in_manuscript")
    op.drop_column("vault_sources", "csl_json")
    op.drop_column("vault_sources", "zotero_version")
    op.drop_column("vault_sources", "zotero_item_key")
    op.drop_column("vault_sources", "zotero_connection_id")

    op.drop_index("ix_chapter_citations_source_id", "chapter_citations")
    op.drop_index("ix_chapter_citations_chapter_id", "chapter_citations")
    op.drop_table("chapter_citations")

    op.drop_index("ix_source_notes_source_id", "source_notes")
    op.drop_table("source_notes")

    op.drop_index("ix_project_citation_styles_book_id", "project_citation_styles")
    op.drop_index("ix_project_citation_styles_project_id", "project_citation_styles")
    op.drop_table("project_citation_styles")

    op.drop_index("ix_citation_styles_slug", "citation_styles")
    op.drop_table("citation_styles")

    op.drop_index("ix_zotero_connections_user_id", "zotero_connections")
    op.drop_table("zotero_connections")
