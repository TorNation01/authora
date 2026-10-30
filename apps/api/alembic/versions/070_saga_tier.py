"""saga tier

Adds the container above a series: one saga, its outline, its constituent
series plans, and the two ledgers that keep a long saga honest (promises made,
truths revealed). Projects gain ``scope`` and ``saga_id`` so a project can be a
standalone book, a series, or a member of a saga. Additive only.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "070"
down_revision = "069"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sagas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sections", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("section_status", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sagas_user_id", "sagas", ["user_id"])

    op.create_table(
        "saga_outlines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "saga_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sagas.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("sections", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "series_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "saga_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sagas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False, server_default="series"),
        sa.Column("sections", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("section_status", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_series_plans_saga_id", "series_plans", ["saga_id"])

    op.create_table(
        "saga_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "saga_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sagas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("opened_in", sa.String(255), nullable=True),
        sa.Column("paid_in", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_saga_threads_saga_id", "saga_threads", ["saga_id"])

    op.create_table(
        "saga_truths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "saga_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sagas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("level", sa.String(20), nullable=False, server_default="saga"),
        sa.Column("status", sa.String(20), nullable=False, server_default="hidden"),
        sa.Column("knows", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column(
            "believes_otherwise", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column("reveal_point", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_saga_truths_saga_id", "saga_truths", ["saga_id"])

    op.add_column("projects", sa.Column("scope", sa.String(20), nullable=False, server_default="series"))
    op.add_column("projects", sa.Column("saga_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_projects_saga_id_sagas",
        "projects",
        "sagas",
        ["saga_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_projects_saga_id", "projects", ["saga_id"])


def downgrade() -> None:
    op.drop_index("ix_projects_saga_id", table_name="projects")
    op.drop_constraint("fk_projects_saga_id_sagas", "projects", type_="foreignkey")
    op.drop_column("projects", "saga_id")
    op.drop_column("projects", "scope")
    op.drop_index("ix_saga_truths_saga_id", table_name="saga_truths")
    op.drop_table("saga_truths")
    op.drop_index("ix_saga_threads_saga_id", table_name="saga_threads")
    op.drop_table("saga_threads")
    op.drop_index("ix_series_plans_saga_id", table_name="series_plans")
    op.drop_table("series_plans")
    op.drop_table("saga_outlines")
    op.drop_index("ix_sagas_user_id", table_name="sagas")
    op.drop_table("sagas")
