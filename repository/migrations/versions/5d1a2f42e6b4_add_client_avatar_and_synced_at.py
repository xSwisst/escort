"""add client avatar_url and profile_synced_at

Revision ID: 5d1a2f42e6b4
Revises: 4c9f1e31d5a3
Create Date: 2026-11-25 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d1a2f42e6b4"
down_revision = "4c9f1e31d5a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("avatar_url", sa.String(length=512), nullable=True))
    op.add_column("clients", sa.Column("profile_synced_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "profile_synced_at")
    op.drop_column("clients", "avatar_url")
