"""email verification for public signup

Adds the proof-of-inbox the product needs before signups can be opened to the
world: an account can be created and used, but checkout stays closed until the
address has been confirmed.

Existing accounts are grandfathered in as verified — they were created by hand,
by invite, or by the founder, and locking them out on deploy would be a bug, not
a security win.

Revision ID: 075
Revises: 074
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "075"
down_revision: Union[str, None] = "074"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean "
        "NOT NULL DEFAULT false"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at "
        "timestamp with time zone"
    )
    # Only the hash of the token is stored: a database leak must not hand out
    # working verification links.
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token_hash "
        "varchar(64)"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at "
        "timestamp with time zone"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_email_verification_token_hash "
        "ON users (email_verification_token_hash)"
    )

    # Grandfather every account that predates this migration. New rows get the
    # column default (false) and must verify.
    op.execute(
        "UPDATE users SET email_verified = true, email_verified_at = now() "
        "WHERE email_verified = false"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_email_verification_token_hash")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verification_sent_at")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verification_token_hash")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified_at")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified")
