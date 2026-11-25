"""add admins and referral fks

Revision ID: 2a9e4c10b3d1
Revises: 1c5f7d9805b9
Create Date: 2026-11-25 13:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a9e4c10b3d1"
down_revision = "1c5f7d9805b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=64), nullable=True),
        sa.Column("last_name", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_admins_telegram_id", "admins", ["telegram_id"], unique=True)

    op.add_column("clients", sa.Column("admin_id", sa.Integer(), nullable=True))
    op.create_index("ix_clients_admin_id", "clients", ["admin_id"], unique=False)
    op.create_foreign_key(
        "fk_clients_admin_id_admins",
        "clients",
        "admins",
        ["admin_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("forms", sa.Column("admin_id", sa.Integer(), nullable=True))
    op.create_index("ix_forms_admin_id", "forms", ["admin_id"], unique=False)
    op.create_foreign_key(
        "fk_forms_admin_id_admins",
        "forms",
        "admins",
        ["admin_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("promotions", sa.Column("admin_id", sa.Integer(), nullable=True))
    op.create_index("ix_promotions_admin_id", "promotions", ["admin_id"], unique=False)
    op.create_foreign_key(
        "fk_promotions_admin_id_admins",
        "promotions",
        "admins",
        ["admin_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("orders", sa.Column("admin_id", sa.Integer(), nullable=True))
    op.create_index("ix_orders_admin_id", "orders", ["admin_id"], unique=False)
    op.create_foreign_key(
        "fk_orders_admin_id_admins",
        "orders",
        "admins",
        ["admin_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_orders_admin_id_admins", "orders", type_="foreignkey")
    op.drop_index("ix_orders_admin_id", table_name="orders")
    op.drop_column("orders", "admin_id")

    op.drop_constraint("fk_promotions_admin_id_admins", "promotions", type_="foreignkey")
    op.drop_index("ix_promotions_admin_id", table_name="promotions")
    op.drop_column("promotions", "admin_id")

    op.drop_constraint("fk_forms_admin_id_admins", "forms", type_="foreignkey")
    op.drop_index("ix_forms_admin_id", table_name="forms")
    op.drop_column("forms", "admin_id")

    op.drop_constraint("fk_clients_admin_id_admins", "clients", type_="foreignkey")
    op.drop_index("ix_clients_admin_id", table_name="clients")
    op.drop_column("clients", "admin_id")

    op.drop_index("ix_admins_telegram_id", table_name="admins")
    op.drop_table("admins")
