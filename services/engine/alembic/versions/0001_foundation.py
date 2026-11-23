"""Create only foundation metadata. No account, funding, or trading state."""

import sqlalchemy as sa

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_metadata",
        sa.Column("key", sa.String(length=80), primary_key=True),
        sa.Column("value", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("system_metadata")
