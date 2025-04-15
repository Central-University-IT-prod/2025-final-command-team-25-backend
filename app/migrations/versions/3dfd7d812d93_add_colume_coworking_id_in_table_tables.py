"""Add colume coworking id in table tables

Revision ID: 3dfd7d812d93
Revises: bcadfc3fc076
Create Date: 2025-03-03 23:06:02.448650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3dfd7d812d93'
down_revision: Union[str, None] = 'bcadfc3fc076'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tables', sa.Column('coworking_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'tables', 'coworkings', ['coworking_id'], ['coworking_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tables', type_='foreignkey')
    op.drop_column('tables', 'coworking_id')
    # ### end Alembic commands ###
