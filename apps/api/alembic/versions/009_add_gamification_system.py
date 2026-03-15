"""Add gamification system tables

Revision ID: 009
Revises: 008
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Badge definitions (static catalog)
    op.create_table(
        "badge_definitions",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("criteria_type", sa.String(50), nullable=False),
        sa.Column("criteria_value", postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Extend achievements with badge_id
    op.add_column("achievements", sa.Column("badge_id", sa.String(50), nullable=True))
    op.add_column("achievements", sa.Column("achievement_metadata", postgresql.JSONB(), nullable=True))

    # Daily quests (generated per user per day)
    op.create_table(
        "daily_quests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quest_date", sa.Date(), nullable=False),
        sa.Column("quest_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("target_value", sa.Integer(), nullable=False),
        sa.Column("current_value", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_quests_user_date", "daily_quests", ["user_id", "quest_date"], unique=False)

    # Weekly missions
    op.create_table(
        "weekly_missions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("mission_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("target_value", sa.Integer(), nullable=False),
        sa.Column("current_value", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weekly_missions_user_week", "weekly_missions", ["user_id", "week_start"], unique=False)

    # Personal bests (daily/weekly word counts)
    op.create_table(
        "personal_bests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("words", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_personal_bests_user_period", "personal_bests", ["user_id", "period_type", "period_start"], unique=True)

    # Focus sessions
    op.create_table(
        "focus_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_minutes", sa.Integer(), nullable=False),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("words_written", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Chapter completion tracking (for gamification rewards)
    op.add_column("chapters", sa.Column("gamification_completed_at", sa.DateTime(timezone=True), nullable=True))

    # User stats extensions for comeback and last_active
    op.add_column("user_stats", sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_stats", sa.Column("best_daily_words", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("user_stats", sa.Column("best_weekly_words", sa.Integer(), nullable=False, server_default="0"))

    # Seed badge definitions
    op.execute(
        """
        INSERT INTO badge_definitions (id, name, description, icon, category, xp_reward, criteria_type, criteria_value, sort_order)
        VALUES
        ('first_word', 'First Word', 'Write your first word', 'pen', 'consistency', 10, 'total_words', '{"min": 1}', 0),
        ('streak_3', 'Three Day Streak', 'Write 3 days in a row', 'flame', 'consistency', 25, 'streak', '{"min": 3}', 1),
        ('streak_7', 'Week Warrior', 'Write 7 days in a row', 'flame', 'consistency', 75, 'streak', '{"min": 7}', 2),
        ('streak_14', 'Fortnight', 'Write 14 days in a row', 'flame', 'consistency', 150, 'streak', '{"min": 14}', 3),
        ('streak_30', 'Monthly Master', 'Write 30 days in a row', 'flame', 'consistency', 300, 'streak', '{"min": 30}', 4),
        ('comeback', 'Welcome Back', 'Return after 7+ days away', 'sunrise', 'consistency', 75, 'comeback', '{"days_away": 7}', 5),
        ('first_chapter', 'Chapter One', 'Complete your first chapter', 'book-open', 'completion', 100, 'chapters_complete', '{"min": 1}', 10),
        ('five_chapters', 'Building Blocks', 'Complete 5 chapters', 'book-open', 'completion', 200, 'chapters_complete', '{"min": 5}', 11),
        ('ten_chapters', 'Decade', 'Complete 10 chapters', 'book-open', 'completion', 400, 'chapters_complete', '{"min": 10}', 12),
        ('10k_words', '10K Club', 'Reach 10,000 words', 'trophy', 'volume', 250, 'total_words', '{"min": 10000}', 20),
        ('25k_words', 'Quarter Draft', 'Reach 25,000 words', 'trophy', 'volume', 500, 'total_words', '{"min": 25000}', 21),
        ('50k_words', 'Half Novel', 'Reach 50,000 words', 'trophy', 'volume', 1000, 'total_words', '{"min": 50000}', 22),
        ('75k_words', 'Three Quarters', 'Reach 75,000 words', 'trophy', 'volume', 1500, 'total_words', '{"min": 75000}', 23),
        ('100k_words', 'Century', 'Reach 100,000 words', 'trophy', 'volume', 2500, 'total_words', '{"min": 100000}', 24),
        ('focus_first', 'Focused Start', 'Complete your first focus session', 'timer', 'focus', 25, 'focus_sessions', '{"min": 1}', 30),
        ('focus_10', 'Deep Work', 'Complete 10 focus sessions', 'timer', 'focus', 100, 'focus_sessions', '{"min": 10}', 31),
        ('focus_25', 'Focus Master', 'Complete 25 focus sessions', 'timer', 'focus', 250, 'focus_sessions', '{"min": 25}', 32),
        ('pb_daily_500', 'Daily 500', 'Write 500 words in a day', 'zap', 'personal_best', 50, 'daily_words', '{"min": 500}', 40),
        ('pb_daily_1000', 'Daily 1K', 'Write 1,000 words in a day', 'zap', 'personal_best', 100, 'daily_words', '{"min": 1000}', 41),
        ('pb_daily_2000', 'Daily 2K', 'Write 2,000 words in a day', 'zap', 'personal_best', 200, 'daily_words', '{"min": 2000}', 42),
        ('pb_weekly_5k', 'Weekly 5K', 'Write 5,000 words in a week', 'zap', 'personal_best', 150, 'weekly_words', '{"min": 5000}', 43),
        ('pb_weekly_10k', 'Weekly 10K', 'Write 10,000 words in a week', 'zap', 'personal_best', 300, 'weekly_words', '{"min": 10000}', 44)
        """
    )


def downgrade() -> None:
    op.drop_column("user_stats", "best_weekly_words")
    op.drop_column("user_stats", "best_daily_words")
    op.drop_column("user_stats", "last_active_at")
    op.drop_column("chapters", "gamification_completed_at")
    op.drop_table("focus_sessions")
    op.drop_index("ix_personal_bests_user_period", table_name="personal_bests")
    op.drop_table("personal_bests")
    op.drop_index("ix_weekly_missions_user_week", table_name="weekly_missions")
    op.drop_table("weekly_missions")
    op.drop_index("ix_daily_quests_user_date", table_name="daily_quests")
    op.drop_table("daily_quests")
    op.drop_column("achievements", "achievement_metadata")
    op.drop_column("achievements", "badge_id")
    op.drop_table("badge_definitions")
