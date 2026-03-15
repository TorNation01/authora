"""Full schema: profiles, preferences, writing styles, book types, phases, sections,
highlights, comments, references, reminders, analytics, publishing assets, feature flags,
soft delete, indexes.

Revision ID: 014
Revises: 013
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Soft delete columns
    op.add_column("projects", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("books", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("chapters", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notes", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Reference tables
    op.create_table(
        "book_types",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "phases",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    # User extensions
    op.create_table(
        "profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "user_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("preferences", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "writing_styles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("voice_tone", sa.String(255), nullable=True),
        sa.Column("style_rules", postgresql.JSONB(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_writing_styles_user_id", "writing_styles", ["user_id"])

    # Book extensions
    op.create_table(
        "book_settings",
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id"),
    )

    # Chapter sections
    op.create_table(
        "chapter_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("content", postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["chapter_sections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapter_sections_chapter_id", "chapter_sections", ["chapter_id"])

    # Content annotations
    op.create_table(
        "content_highlights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_highlights_chapter_id", "content_highlights", ["chapter_id"])
    op.create_index("ix_content_highlights_note_id", "content_highlights", ["note_id"])

    op.create_table(
        "content_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["content_comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_comments_chapter_id", "content_comments", ["chapter_id"])
    op.create_index("ix_content_comments_note_id", "content_comments", ["note_id"])

    # Reference items
    op.create_table(
        "reference_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ref_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("url", sa.String(2000), nullable=True),
        sa.Column("citation_text", sa.Text(), nullable=True),
        sa.Column("ref_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reference_items_book_id", "reference_items", ["book_id"])
    op.create_index("ix_reference_items_project_id", "reference_items", ["project_id"])

    # AI action registry
    op.create_table(
        "ai_action_registry",
        sa.Column("id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("requires_selection", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config_schema", postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Ghostwriter sessions
    op.create_table(
        "ghostwriter_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ghostwriter_workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_type", sa.String(50), nullable=False),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("output_summary", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["ghostwriter_workspace_id"], ["ghostwriter_workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ghostwriter_sessions_workspace_id", "ghostwriter_sessions", ["ghostwriter_workspace_id"])

    # Reminders
    op.create_table(
        "reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reminder_type", sa.String(50), nullable=False),
        sa.Column("scheduled_time", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])

    # Analytics events
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
    op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])

    # Publishing assets
    op.create_table(
        "publishing_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=True),
        sa.Column("asset_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publishing_assets_book_id", "publishing_assets", ["book_id"])

    # Setup state
    op.create_table(
        "setup_state",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("key"),
    )

    # Feature flags
    op.create_table(
        "feature_flags",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rules", postgresql.JSONB(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("key"),
    )

    # Indexes for soft delete
    op.create_index("ix_books_deleted_at", "books", ["deleted_at"])
    op.create_index("ix_chapters_deleted_at", "chapters", ["deleted_at"])
    op.create_index("ix_notes_deleted_at", "notes", ["deleted_at"])
    op.create_index("ix_projects_deleted_at", "projects", ["deleted_at"])

    # Audit log index
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # Seed reference data
    op.execute(
        """
        INSERT INTO book_types (id, name, description, sort_order)
        VALUES
        ('fiction', 'Fiction', 'Novels, short stories, creative writing', 0),
        ('nonfiction', 'Non-Fiction', 'Memoir, how-to, business, self-help', 1)
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO phases (id, name, description, sort_order)
        VALUES
        ('idea', 'Idea', 'Capture and refine your concept', 0),
        ('concept', 'Concept', 'Develop premise and structure', 1),
        ('outline', 'Outline', 'Create chapter outline', 2),
        ('chapter_planning', 'Chapter Planning', 'Plan scenes and beats', 3),
        ('drafting', 'Drafting', 'Write first draft', 4),
        ('revision', 'Revision', 'Revise and edit', 5),
        ('polish', 'Polish', 'Final polish and proofread', 6),
        ('export_prep', 'Export Prep', 'Prepare for publishing', 7)
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO ai_action_registry (id, name, description, category, requires_selection, sort_order, is_public)
        VALUES
        ('rewrite', 'Rewrite', 'Rewrite selected text in a different style', 'editing', true, 0, true),
        ('expand', 'Expand', 'Expand selected text with more detail', 'editing', true, 1, true),
        ('shorten', 'Shorten', 'Condense selected text', 'editing', true, 2, true),
        ('improve', 'Improve', 'Improve clarity and flow', 'editing', true, 3, true),
        ('fix_grammar', 'Fix Grammar', 'Correct grammar and punctuation', 'editing', true, 4, true),
        ('suggest', 'Suggest', 'Suggest alternative phrasing', 'editing', true, 5, true),
        ('tone_formal', 'Make Formal', 'Make tone more formal', 'tone', true, 10, true),
        ('tone_casual', 'Make Casual', 'Make tone more casual', 'tone', true, 11, true),
        ('continue', 'Continue', 'Continue writing from selection', 'generation', false, 20, true)
        ON CONFLICT (id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_projects_deleted_at", table_name="projects")
    op.drop_index("ix_notes_deleted_at", table_name="notes")
    op.drop_index("ix_chapters_deleted_at", table_name="chapters")
    op.drop_index("ix_books_deleted_at", table_name="books")

    op.drop_table("feature_flags")
    op.drop_table("setup_state")
    op.drop_index("ix_publishing_assets_book_id", table_name="publishing_assets")
    op.drop_table("publishing_assets")
    op.drop_index("ix_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("ix_analytics_events_event_type", table_name="analytics_events")
    op.drop_index("ix_analytics_events_user_id", table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_table("reminders")
    op.drop_index("ix_ghostwriter_sessions_workspace_id", table_name="ghostwriter_sessions")
    op.drop_table("ghostwriter_sessions")
    op.drop_table("ai_action_registry")
    op.drop_index("ix_reference_items_project_id", table_name="reference_items")
    op.drop_index("ix_reference_items_book_id", table_name="reference_items")
    op.drop_table("reference_items")
    op.drop_index("ix_content_comments_note_id", table_name="content_comments")
    op.drop_index("ix_content_comments_chapter_id", table_name="content_comments")
    op.drop_table("content_comments")
    op.drop_index("ix_content_highlights_note_id", table_name="content_highlights")
    op.drop_index("ix_content_highlights_chapter_id", table_name="content_highlights")
    op.drop_table("content_highlights")
    op.drop_index("ix_chapter_sections_chapter_id", table_name="chapter_sections")
    op.drop_table("chapter_sections")
    op.drop_table("book_settings")
    op.drop_index("ix_writing_styles_user_id", table_name="writing_styles")
    op.drop_table("writing_styles")
    op.drop_table("user_preferences")
    op.drop_table("profiles")
    op.drop_table("phases")
    op.drop_table("book_types")

    op.drop_column("notes", "deleted_at")
    op.drop_column("chapters", "deleted_at")
    op.drop_column("books", "deleted_at")
    op.drop_column("projects", "deleted_at")
