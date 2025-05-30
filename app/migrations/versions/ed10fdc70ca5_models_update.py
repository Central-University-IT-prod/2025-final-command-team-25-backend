"""Models update

Revision ID: ed10fdc70ca5
Revises: a7802ff39415
Create Date: 2025-03-01 12:57:03.889162

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ed10fdc70ca5"
down_revision: Union[str, None] = "a7802ff39415"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tables",
        sa.Column("table_id", sa.Uuid(), nullable=False),
        sa.Column("pos_x", sa.Float(), nullable=False),
        sa.Column("pos_y", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("table_id"),
    )
    op.create_table(
        "seat_bookings",
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("seat_id", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.booking_id"],
        ),
        sa.ForeignKeyConstraint(
            ["seat_id"],
            ["seats.seat_id"],
        ),
        sa.PrimaryKeyConstraint("booking_id", "seat_id"),
    )

    # Explicitly cast start_date and end_date to TIMESTAMP WITH TIME ZONE
    op.execute(
        "ALTER TABLE bookings ALTER COLUMN start_date TYPE TIMESTAMP WITH TIME ZONE USING start_date::timestamp with time zone"
    )
    op.execute(
        "ALTER TABLE bookings ALTER COLUMN end_date TYPE TIMESTAMP WITH TIME ZONE USING end_date::timestamp with time zone"
    )

    op.drop_constraint("bookings_seat_id_fkey", "bookings", type_="foreignkey")
    op.drop_column("bookings", "coworking_id")
    op.drop_column("bookings", "seat_id")
    op.add_column("seats", sa.Column("booking_id", sa.Uuid(), nullable=False))
    op.add_column("seats", sa.Column("table_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(None, "seats", "bookings", ["booking_id"], ["booking_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "seats", type_="foreignkey")
    op.drop_column("seats", "table_id")
    op.drop_column("seats", "booking_id")
    op.add_column(
        "bookings", sa.Column("seat_id", sa.UUID(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "bookings",
        sa.Column("coworking_id", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "bookings_seat_id_fkey", "bookings", "seats", ["seat_id"], ["seat_id"]
    )

    # Convert back to VARCHAR if downgrading
    op.execute(
        "ALTER TABLE bookings ALTER COLUMN end_date TYPE VARCHAR USING end_date::text"
    )
    op.execute(
        "ALTER TABLE bookings ALTER COLUMN start_date TYPE VARCHAR USING start_date::text"
    )

    op.drop_table("seat_bookings")
    op.drop_table("tables")
    # ### end Alembic commands ###
