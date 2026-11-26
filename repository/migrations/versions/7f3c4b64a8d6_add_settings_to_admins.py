"""add settings jsonb to admins

Revision ID: 7f3c4b64a8d6
Revises: 6e2b3a53f7c5
Create Date: 2026-11-26 16:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "7f3c4b64a8d6"
down_revision = "6e2b3a53f7c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "admins",
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("admins", "settings")
