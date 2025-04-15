"""Add user id for seat bookings

Revision ID: 1f605e6db5ff
Revises: 2f999816de8c
Create Date: 2025-03-03 10:11:39.291921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1f605e6db5ff'
down_revision: Union[str, None] = '2f999816de8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seat_bookings', sa.Column('user_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'seat_bookings', 'users', ['user_id'], ['client_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'seat_bookings', type_='foreignkey')
    op.drop_column('seat_bookings', 'user_id')
    # ### end Alembic commands ###
