"""add client is_pinned and last_active_at

Revision ID: 6e2b3a53f7c5
Revises: 5d1a2f42e6b4
Create Date: 2026-11-25 18:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6e2b3a53f7c5"
down_revision = "5d1a2f42e6b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("is_pinned", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("clients", sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "last_active_at")
    op.drop_column("clients", "is_pinned")
