"""Add originality, similarity, AI-assistance transparency, and AI-origin risk review system.

Revision ID: 051
Revises: 050
Create Date: 2025-03-15

Similarity engine, comparison corpora, matched passages, AI-assistance disclosure,
AI-origin risk review, educator/reviewer workflow, admin controls.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "051"
down_revision: Union[str, None] = "050"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Comparison corpora (user-owned, uploaded, course, reference)
    op.create_table(
        "comparison_corpora",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("corpus_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comparison_corpora_project_id", "comparison_corpora", ["project_id"])
    op.create_index("ix_comparison_corpora_user_id", "comparison_corpora", ["user_id"])

    # Originality scans
    op.create_table(
        "originality_scans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("overall_similarity_pct", sa.Float(), nullable=True),
        sa.Column("excluded_ranges", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("corpus_ids", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_originality_scans_project_id", "originality_scans", ["project_id"])
    op.create_index("ix_originality_scans_book_id", "originality_scans", ["book_id"])

    # Matched passages (similarity results)
    op.create_table(
        "matched_passages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scan_id", sa.UUID(), nullable=False),
        sa.Column("chapter_id", sa.UUID(), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_label", sa.String(500), nullable=True),
        sa.Column("match_type", sa.String(50), nullable=False),
        sa.Column("similarity_pct", sa.Float(), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("matched_text", sa.Text(), nullable=False),
        sa.Column("query_start", sa.Integer(), nullable=True),
        sa.Column("query_end", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["originality_scans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matched_passages_scan_id", "matched_passages", ["scan_id"])

    # AI-assistance disclosure (user-disclosed or system-tracked)
    op.create_table(
        "ai_assistance_disclosures",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=True),
        sa.Column("chapter_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("disclosure_type", sa.String(50), nullable=False),
        sa.Column("content_source", sa.String(50), nullable=True),
        sa.Column("ai_action_id", sa.UUID(), nullable=True),
        sa.Column("section_hint", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ai_action_id"], ["ai_action_log.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_assistance_disclosures_project_id", "ai_assistance_disclosures", ["project_id"])
    op.create_index("ix_ai_assistance_disclosures_chapter_id", "ai_assistance_disclosures", ["chapter_id"])

    # AI-origin risk reviews (probabilistic, review-aid only)
    op.create_table(
        "ai_origin_risk_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("chapter_id", sa.UUID(), nullable=True),
        sa.Column("risk_band", sa.String(50), nullable=False),
        sa.Column("confidence_low", sa.Float(), nullable=True),
        sa.Column("confidence_high", sa.Float(), nullable=True),
        sa.Column("signals_summary", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("disclaimer_ack", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_origin_risk_reviews_project_id", "ai_origin_risk_reviews", ["project_id"])

    # Review reports (educator/reviewer workflow)
    op.create_table(
        "integrity_review_reports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("originality_scan_id", sa.UUID(), nullable=True),
        sa.Column("reviewer_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("needs_human_review", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["originality_scan_id"], ["originality_scans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_integrity_review_reports_project_id", "integrity_review_reports", ["project_id"])

    # Review comments (source-by-source, reviewer feedback)
    op.create_table(
        "integrity_review_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("report_id", sa.UUID(), nullable=False),
        sa.Column("matched_passage_id", sa.UUID(), nullable=True),
        sa.Column("comment_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["integrity_review_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["matched_passage_id"], ["matched_passages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_integrity_review_comments_report_id", "integrity_review_comments", ["report_id"])

    # Admin originality config (corpora, exclusions, feature flags)
    op.create_table(
        "originality_admin_config",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_originality_admin_config_key", "originality_admin_config", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_originality_admin_config_key", "originality_admin_config")
    op.drop_table("originality_admin_config")
    op.drop_index("ix_integrity_review_comments_report_id", "integrity_review_comments")
    op.drop_table("integrity_review_comments")
    op.drop_index("ix_integrity_review_reports_project_id", "integrity_review_reports")
    op.drop_table("integrity_review_reports")
    op.drop_index("ix_ai_origin_risk_reviews_project_id", "ai_origin_risk_reviews")
    op.drop_table("ai_origin_risk_reviews")
    op.drop_index("ix_ai_assistance_disclosures_chapter_id", "ai_assistance_disclosures")
    op.drop_index("ix_ai_assistance_disclosures_project_id", "ai_assistance_disclosures")
    op.drop_table("ai_assistance_disclosures")
    op.drop_index("ix_matched_passages_scan_id", "matched_passages")
    op.drop_table("matched_passages")
    op.drop_index("ix_originality_scans_book_id", "originality_scans")
    op.drop_index("ix_originality_scans_project_id", "originality_scans")
    op.drop_table("originality_scans")
    op.drop_index("ix_comparison_corpora_user_id", "comparison_corpora")
    op.drop_index("ix_comparison_corpora_project_id", "comparison_corpora")
    op.drop_table("comparison_corpora")
