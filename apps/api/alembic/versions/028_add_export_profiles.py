"""Add export profiles.

Revision ID: 028
Revises: 027
Create Date: 2025-03-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "028"
down_revision: Union[str, None] = "027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "export_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("system_key", sa.String(50), nullable=True),
        sa.Column("format", sa.String(20), nullable=False, server_default="docx"),
        sa.Column("compile_type", sa.String(50), nullable=False, server_default="full"),
        sa.Column("format_style", sa.String(20), nullable=False, server_default="manuscript"),
        sa.Column("options", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("front_matter_blocks", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("back_matter_blocks", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("naming_pattern", sa.String(200), nullable=True),
        sa.Column("project_type", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_export_profiles_user_id", "export_profiles", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_export_profiles_user_id", table_name="export_profiles")
    op.drop_table("export_profiles")
