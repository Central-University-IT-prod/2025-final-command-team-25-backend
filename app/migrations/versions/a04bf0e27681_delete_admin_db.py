"""delete admin db

Revision ID: a04bf0e27681
Revises: 0e47abfac657
Create Date: 2025-03-04 01:13:08.682761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a04bf0e27681'
down_revision: Union[str, None] = '0e47abfac657'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admins')



def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('admin_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('coworking_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['users.client_id'], name='admins_admin_id_fkey'),
    sa.ForeignKeyConstraint(['coworking_id'], ['coworkings.coworking_id'], name='admins_coworking_id_fkey'),
    sa.PrimaryKeyConstraint('admin_id', name='admins_pkey')
    )
    # ### end Alembic commands ###
