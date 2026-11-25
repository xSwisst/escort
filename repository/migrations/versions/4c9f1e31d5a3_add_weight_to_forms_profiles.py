"""add weight to forms_profiles

Revision ID: 4c9f1e31d5a3
Revises: 3b8e9d20c4f2
Create Date: 2026-11-25 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4c9f1e31d5a3"
down_revision = "3b8e9d20c4f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("forms_profiles", sa.Column("weight", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("forms_profiles", "weight")
