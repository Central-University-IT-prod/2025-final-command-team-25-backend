"""changed id for seats

Revision ID: 7f848b9e3b51
Revises: 6214c48f418f
Create Date: 2025-03-01 23:02:36.330883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7f848b9e3b51'
down_revision: Union[str, None] = '6214c48f418f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Add new integer column for seat_id
    op.add_column('seats', sa.Column('new_seat_id', sa.Integer(), autoincrement=True))

    # Create a temporary sequence for IDs if needed
    conn.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS seats_id_seq START 1"))

    # Populate new_seat_id with sequential numbers
    conn.execute(sa.text("""
        UPDATE seats
        SET new_seat_id = nextval('seats_id_seq')
    """))

    # Add new column to seat_bookings for mapping
    op.add_column('seat_bookings', sa.Column('new_seat_id', sa.Integer(), nullable=True))

    # Update seat_bookings with mapped seat_id values
    conn.execute(sa.text("""
        UPDATE seat_bookings sb
        SET new_seat_id = s.new_seat_id
        FROM seats s
        WHERE sb.seat_id = s.seat_id
    """))

    # Drop old UUID-based foreign key (if exists)
    op.drop_constraint('seat_bookings_seat_id_fkey', 'seat_bookings', type_='foreignkey')

    # Drop old columns
    op.drop_column('seat_bookings', 'seat_id')
    op.drop_column('seats', 'seat_id')

    # Rename new columns to the old names
    op.alter_column('seats', 'new_seat_id', new_column_name='seat_id')
    op.alter_column('seat_bookings', 'new_seat_id', new_column_name='seat_id')

    # Recreate foreign key on seat_bookings
    # op.create_foreign_key(
    #     'seat_bookings_seat_id_fkey', 'seat_bookings', 'seats', ['seat_id'], ['seat_id']
    # )

    # Drop sequence if you don't need it anymore
    conn.execute(sa.text("DROP SEQUENCE IF EXISTS seats_id_seq"))

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coworkings', sa.Column('address', sa.String(), nullable=False, server_default=''))

    op.add_column('seat_bookings', sa.Column('seat_uuid', sa.UUID(), nullable=False))
    op.alter_column('seat_bookings', 'seat_id',
                    existing_type=sa.UUID(),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.drop_column('seat_bookings', 'token')
    op.drop_column('seats', 'pos')
    # ### end Alembic commands ###


def downgrade() -> None:
    conn = op.get_bind()

    # 1. Add back the UUID column (it was dropped during upgrade)
    op.add_column('seats', sa.Column('old_seat_id', postgresql.UUID(), nullable=False))

    # 2. Populate it using the stored seat_uuid column
    conn.execute(sa.text("""
        UPDATE seats
        SET old_seat_id = seat_uuid
    """))

    # 3. Rename old_seat_id back to seat_id
    op.drop_column('seats', 'seat_id')
    op.alter_column('seats', 'old_seat_id', new_column_name='seat_id')

    # 4. Restore seat_bookings.seat_id (if needed for relations)
    op.add_column('seat_bookings', sa.Column('old_seat_id', postgresql.UUID(), nullable=True))

    conn.execute(sa.text("""
        UPDATE seat_bookings sb
        SET old_seat_id = s.seat_id
        FROM seats s
        WHERE sb.seat_id = s.seat_id
    """))

    # 5. Drop current (int) seat_id and rename old_seat_id back to seat_id
    op.drop_column('seat_bookings', 'seat_id')
    op.alter_column('seat_bookings', 'old_seat_id', new_column_name='seat_id')

    # 6. Drop seat_uuid column if you want to clean up
    op.drop_column('seats', 'seat_uuid')

    # 7. Recreate foreign key if needed
    op.create_foreign_key(
        'seat_bookings_seat_id_fkey', 'seat_bookings', 'seats', ['seat_id'], ['seat_id']
    )

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seats',
                  sa.Column('pos', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('seat_bookings', sa.Column('token', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.alter_column('seat_bookings', 'seat_id',
                    existing_type=sa.Integer(),
                    type_=sa.UUID(),
                    existing_nullable=False)
    op.drop_column('seat_bookings', 'seat_uuid')
    op.drop_column('coworkings', 'address')
    # ### end Alembic commands ###
