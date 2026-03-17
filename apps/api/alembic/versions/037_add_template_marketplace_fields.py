"""Add template marketplace future-ready fields.

Revision ID: 037
Revises: 036
Create Date: 2026-03-15

Future-ready for paid templates and creator uploads:
- price_cents: nullable, for paid templates
- is_paid: boolean, default false
- creator_id: nullable, for creator attribution (admin-controlled initially)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "037"
down_revision: Union[str, None] = "036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("project_templates", sa.Column("price_cents", sa.Integer(), nullable=True))
    op.add_column("project_templates", sa.Column("is_paid", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("project_templates", sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_project_templates_creator_id",
        "project_templates",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_project_templates_creator_id", "project_templates", ["creator_id"])
    op.create_index("ix_project_templates_is_paid", "project_templates", ["is_paid"])


def downgrade() -> None:
    op.drop_index("ix_project_templates_is_paid", table_name="project_templates")
    op.drop_index("ix_project_templates_creator_id", table_name="project_templates")
    op.drop_constraint("fk_project_templates_creator_id", "project_templates", type_="foreignkey")
    op.drop_column("project_templates", "creator_id")
    op.drop_column("project_templates", "is_paid")
    op.drop_column("project_templates", "price_cents")
