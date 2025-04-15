"""Fix something

Revision ID: 987f66ee49b5
Revises: 3c8e35326f76
Create Date: 2025-03-03 21:26:38.294448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '987f66ee49b5'
down_revision: Union[str, None] = '3c8e35326f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Old and new enums
old_enum = sa.Enum('GUEST', 'STUDENT', 'ADMIN', name='verificationlevel')
new_enum = sa.Enum('GUEST', 'STANDARD', 'PRO', name='verificationlevel')


def upgrade() -> None:
    # Drop tables in reverse order of dependency (to avoid FK constraint issues)
    op.execute('DELETE FROM admins')
    op.execute('DELETE FROM seat_bookings')
    op.execute('DELETE FROM bookings')
    op.execute('DELETE FROM seats')
    op.execute('DELETE FROM users')

    # Add new column with new enum type
    op.drop_column('users', 'verification_level')

    # Create the new enum type
    new_enum.create(op.get_bind(), checkfirst=True)

    # Add the new verification_level column with the new enum type
    op.add_column('users', sa.Column('verification_level', new_enum, nullable=False, server_default='GUEST'))


def downgrade() -> None:
    pass
