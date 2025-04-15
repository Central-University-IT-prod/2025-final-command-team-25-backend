"""Fix tables and seats

Revision ID: 92a717ba60b1
Revises: ed10fdc70ca5
Create Date: 2025-03-01 14:55:07.956368

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "92a717ba60b1"
down_revision: Union[str, None] = "ed10fdc70ca5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new table 'coworkings'
    op.create_table(
        "coworkings",
        sa.Column("coworking_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("coworking_id"),
    )

    # Drop the old 'tables' table
    op.drop_table("tables")

    # Add new columns to 'seats'
    op.add_column(
        "seats", sa.Column("pos_x", sa.Float(), nullable=False, server_default="0.0")
    )
    op.add_column(
        "seats", sa.Column("pos_y", sa.Float(), nullable=False, server_default="0.0")
    )

    # Add new 'pos' column with a default of 0
    op.add_column(
        "seats", sa.Column("pos", sa.Integer(), nullable=False, server_default="0")
    )

    # Set 'pos' to 0 for existing rows
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE seats SET pos = 0"))

    # Change the column type for 'coworking_id'
    op.execute(
        "ALTER TABLE seats ALTER COLUMN coworking_id TYPE UUID USING coworking_id::uuid"
    )

    # Update foreign key constraints
    op.drop_constraint("seats_booking_id_fkey", "seats", type_="foreignkey")
    op.create_foreign_key(
        None, "seats", "coworkings", ["coworking_id"], ["coworking_id"]
    )

    # Drop unused columns from 'seats'
    op.drop_column("seats", "seat_type")
    op.drop_column("seats", "table_id")
    op.drop_column("seats", "booking_id")


def downgrade() -> None:
    # Re-add dropped columns
    op.add_column(
        "seats", sa.Column("booking_id", sa.UUID(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "seats", sa.Column("table_id", sa.UUID(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "seats",
        sa.Column(
            "seat_type",
            postgresql.ENUM("AUDIENCE", "OPENSPACE", name="seattype"),
            autoincrement=False,
            nullable=False,
        ),
    )

    # Drop the added 'pos' column
    op.drop_column("seats", "pos")

    # Recreate the old foreign key
    op.drop_constraint(None, "seats", type_="foreignkey")
    op.create_foreign_key(
        "seats_booking_id_fkey", "seats", "bookings", ["booking_id"], ["booking_id"]
    )

    # Revert the column type change for 'coworking_id'
    op.alter_column(
        "seats",
        "coworking_id",
        existing_type=sa.UUID(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
    )

    # Drop new columns
    op.drop_column("seats", "pos_y")
    op.drop_column("seats", "pos_x")

    # Recreate 'tables' table
    op.create_table(
        "tables",
        sa.Column("table_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "pos_x",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "pos_y",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("table_id", name="tables_pkey"),
    )

    # Drop 'coworkings' table
    op.drop_table("coworkings")
