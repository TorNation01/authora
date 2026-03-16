"""Add AUTHORA vault tables.

Revision ID: 031
Revises: 030
Create Date: 2025-03-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "031"
down_revision: Union[str, None] = "030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vault_characters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("aliases", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("role_in_story", sa.String(255), nullable=True),
        sa.Column("archetype", sa.String(100), nullable=True),
        sa.Column("age", sa.String(100), nullable=True),
        sa.Column("appearance_notes", sa.Text(), nullable=True),
        sa.Column("voice_notes", sa.Text(), nullable=True),
        sa.Column("personality_traits", sa.Text(), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("fears", sa.Text(), nullable=True),
        sa.Column("motivations", sa.Text(), nullable=True),
        sa.Column("internal_conflict", sa.Text(), nullable=True),
        sa.Column("external_conflict", sa.Text(), nullable=True),
        sa.Column("backstory", sa.Text(), nullable=True),
        sa.Column("timeline_notes", sa.Text(), nullable=True),
        sa.Column("secrets", sa.Text(), nullable=True),
        sa.Column("quirks", sa.Text(), nullable=True),
        sa.Column("dialogue_patterns", sa.Text(), nullable=True),
        sa.Column("emotional_arc", sa.Text(), nullable=True),
        sa.Column("private_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_characters_project_id", "vault_characters", ["project_id"])
    op.create_index("ix_vault_characters_book_id", "vault_characters", ["book_id"])

    op.create_table(
        "vault_locations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=False, server_default="location"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rules", sa.Text(), nullable=True),
        sa.Column("geography", sa.Text(), nullable=True),
        sa.Column("environment", sa.Text(), nullable=True),
        sa.Column("atmosphere", sa.Text(), nullable=True),
        sa.Column("history", sa.Text(), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["vault_locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_locations_project_id", "vault_locations", ["project_id"])

    op.create_table(
        "vault_timeline_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False, server_default="story_event"),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("date_label", sa.String(255), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("storyline", sa.String(255), nullable=True),
        sa.Column("time_period", sa.String(255), nullable=True),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_timeline_events_project_id", "vault_timeline_events", ["project_id"])

    op.create_table(
        "vault_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("author", sa.String(500), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="book"),
        sa.Column("publication_date", sa.String(100), nullable=True),
        sa.Column("url", sa.String(2000), nullable=True),
        sa.Column("link_metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("usage_notes", sa.Text(), nullable=True),
        sa.Column("topic_tags", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("quote_extracts", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("citation_notes", sa.Text(), nullable=True),
        sa.Column("reliability_note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="needs_review"),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_sources_project_id", "vault_sources", ["project_id"])

    op.create_table(
        "vault_ideas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("chapter_id", sa.Uuid(), nullable=True),
        sa.Column("character_id", sa.Uuid(), nullable=True),
        sa.Column("location_id", sa.Uuid(), nullable=True),
        sa.Column("timeline_event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("idea_type", sa.String(50), nullable=False, server_default="idea_card"),
        sa.Column("status", sa.String(50), nullable=False, server_default="raw_idea"),
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("starred", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["character_id"], ["vault_characters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["location_id"], ["vault_locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["vault_timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_ideas_project_id", "vault_ideas", ["project_id"])
    op.create_index("ix_vault_ideas_status", "vault_ideas", ["status"])

    op.create_table(
        "vault_research_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("entry_type", sa.String(50), nullable=False, server_default="note"),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("tags", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("needs_verification", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("link_metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["vault_research_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["vault_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_research_entries_project_id", "vault_research_entries", ["project_id"])

    op.create_table(
        "vault_relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("character_a_id", sa.Uuid(), nullable=False),
        sa.Column("character_b_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(100), nullable=True),
        sa.Column("history", sa.Text(), nullable=True),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_a_id"], ["vault_characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_b_id"], ["vault_characters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_relationships_project_id", "vault_relationships", ["project_id"])

    op.create_table(
        "vault_themes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("theme_type", sa.String(50), nullable=False, server_default="theme"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_central", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("extra", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vault_themes_project_id", "vault_themes", ["project_id"])

    op.create_table(
        "chapter_character_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["vault_characters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_character_links_chapter_id", "chapter_character_links", ["chapter_id"])

    op.create_table(
        "chapter_location_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("location_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["vault_locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_location_links_chapter_id", "chapter_location_links", ["chapter_id"])

    op.create_table(
        "chapter_event_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["vault_timeline_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_event_links_chapter_id", "chapter_event_links", ["chapter_id"])

    op.create_table(
        "chapter_theme_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("theme_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["theme_id"], ["vault_themes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_theme_links_chapter_id", "chapter_theme_links", ["chapter_id"])

    op.create_table(
        "chapter_source_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("usage_notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["vault_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_source_links_chapter_id", "chapter_source_links", ["chapter_id"])

    op.create_table(
        "chapter_research_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("research_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["vault_research_entries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_research_links_chapter_id", "chapter_research_links", ["chapter_id"])


def downgrade() -> None:
    op.drop_table("chapter_research_links")
    op.drop_table("chapter_source_links")
    op.drop_table("chapter_theme_links")
    op.drop_table("chapter_event_links")
    op.drop_table("chapter_location_links")
    op.drop_table("chapter_character_links")
    op.drop_table("vault_themes")
    op.drop_table("vault_relationships")
    op.drop_table("vault_research_entries")
    op.drop_table("vault_ideas")
    op.drop_table("vault_sources")
    op.drop_table("vault_timeline_events")
    op.drop_table("vault_locations")
    op.drop_table("vault_characters")
