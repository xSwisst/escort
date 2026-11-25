"""add cities and client_cities

Revision ID: 3b8e9d20c4f2
Revises: 2a9e4c10b3d1
Create Date: 2026-11-25 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3b8e9d20c4f2"
down_revision = "2a9e4c10b3d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cities_name", "cities", ["name"], unique=True)

    op.create_table(
        "client_cities",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), autoincrement=True, nullable=False),
        sa.Column("client_id", sa.BigInteger(), nullable=False),
        sa.Column("city_id", sa.Integer(), nullable=True),
        sa.Column("city_name", sa.String(length=128), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id", "slot", name="uq_client_cities_client_slot"),
    )
    op.create_index("ix_client_cities_client_id", "client_cities", ["client_id"], unique=False)
    op.create_index("ix_client_cities_city_id", "client_cities", ["city_id"], unique=False)

    op.add_column("forms_publication", sa.Column("city_id", sa.Integer(), nullable=True))
    op.add_column(
        "forms_publication",
        sa.Column("is_static", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index("ix_forms_publication_city_id", "forms_publication", ["city_id"], unique=False)
    op.create_index("ix_forms_publication_is_static", "forms_publication", ["is_static"], unique=False)
    op.create_foreign_key(
        "fk_forms_publication_city_id_cities",
        "forms_publication",
        "cities",
        ["city_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Backfill existing primary_city / secondary_city into client_cities
    op.execute(
        """
        INSERT INTO client_cities (client_id, city_name, slot, is_active)
        SELECT user_id, primary_city, 1, (active_city_slot = 1 OR secondary_city IS NULL)
        FROM clients
        WHERE primary_city IS NOT NULL AND primary_city <> ''
        ON CONFLICT (client_id, slot) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO client_cities (client_id, city_name, slot, is_active)
        SELECT user_id, secondary_city, 2, (active_city_slot = 2)
        FROM clients
        WHERE secondary_city IS NOT NULL AND secondary_city <> ''
        ON CONFLICT (client_id, slot) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_forms_publication_city_id_cities", "forms_publication", type_="foreignkey")
    op.drop_index("ix_forms_publication_is_static", table_name="forms_publication")
    op.drop_index("ix_forms_publication_city_id", table_name="forms_publication")
    op.drop_column("forms_publication", "is_static")
    op.drop_column("forms_publication", "city_id")

    op.drop_index("ix_client_cities_city_id", table_name="client_cities")
    op.drop_index("ix_client_cities_client_id", table_name="client_cities")
    op.drop_table("client_cities")

    op.drop_index("ix_cities_name", table_name="cities")
    op.drop_table("cities")
