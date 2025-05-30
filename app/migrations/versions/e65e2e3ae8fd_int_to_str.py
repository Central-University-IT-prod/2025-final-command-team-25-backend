"""Int to str

Revision ID: e65e2e3ae8fd
Revises: 63006692c655
Create Date: 2025-03-02 13:29:40.912533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e65e2e3ae8fd'
down_revision: Union[str, None] = '63006692c655'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('seats', 'seat_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.drop_constraint('seats_seat_uuid_key', 'seats', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('seats_seat_uuid_key', 'seats', ['seat_uuid'])
    op.alter_column('seats', 'seat_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
