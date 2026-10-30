"""profitability targets and monthly snapshots

Two additive tables, nothing existing changes:

* `profitability_targets` — one row, the numbers the business is held to.
  Seeded here from the strategy decision (build to profitability, $2k MRR),
  so the target is durable and reproducible rather than a note in chat.
* `profitability_snapshots` — one row per calendar month, written by
  `scripts/profitability.py snapshot` on the first of the month. MRR, churn
  and CAC only mean something as a series; a single live query proves nothing
  about last month.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "073"
down_revision = "072"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profitability_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("mrr_target_cents", sa.Integer(), nullable=False),
        sa.Column("churn_target_bps", sa.Integer(), nullable=False),
        sa.Column("cac_target_cents", sa.Integer(), nullable=False),
        sa.Column("arpu_benchmark_cents", sa.Integer(), nullable=False, server_default="2235"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "profitability_snapshots",
        sa.Column("month", sa.Date(), primary_key=True, nullable=False),
        sa.Column("mrr_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_recurring_subs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_lifetime_subs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_paid_subs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churned_subs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churn_bps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("arpu_cents", sa.Integer(), nullable=True),
        sa.Column("marketing_spend_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cac_cents", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="manual"),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute(
        """
        INSERT INTO profitability_targets
            (id, mrr_target_cents, churn_target_bps, cac_target_cents, arpu_benchmark_cents, notes)
        VALUES
            (gen_random_uuid(), 200000, 500, 6700, 2235,
             'Build to profitability (2026-10-30). $2,000 MRR = 90 subs at $22.35 blended ARPU; '
             '<=5% monthly logo churn; CAC <= $67 for <=3 month payback.')
        """
    )


def downgrade() -> None:
    op.drop_table("profitability_snapshots")
    op.drop_table("profitability_targets")
