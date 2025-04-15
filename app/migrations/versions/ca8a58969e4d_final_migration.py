"""final migration

Revision ID: ca8a58969e4d
Revises: b07934f78e11
Create Date: 2025-03-03 02:07:10.293441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ca8a58969e4d'
down_revision: Union[str, None] = 'b07934f78e11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Создаём новый тип Enum
    user_access_level_enum = sa.Enum('GUEST', 'STUDENT', 'ADMIN', name='useraccesslevel')
    user_access_level_enum.create(op.get_bind())

    # Изменяем тип колонки `access_level` с явным указанием USING
    op.execute('''
        ALTER TABLE users
        ALTER COLUMN access_level
        TYPE useraccesslevel
        USING access_level::text::useraccesslevel
    ''')


    # Изменяем тип колонки `verification_level` с явным указанием USING
    op.execute('''
        ALTER TABLE users
        ALTER COLUMN verification_level
        TYPE seataccesslevel
        USING verification_level::text::seataccesslevel
    ''')

    # Удаляем старый тип Enum, если он больше не используется
    op.execute("DROP TYPE IF EXISTS user_status_enum")


def downgrade() -> None:
    # Восстанавливаем старый тип Enum для `access_level`
    old_user_status_enum = postgresql.ENUM('GUEST', 'STUDENT', 'ADMIN', name='user_status_enum')
    old_user_status_enum.create(op.get_bind())

    op.execute('''
        ALTER TABLE users
        ALTER COLUMN access_level
        TYPE user_status_enum
        USING access_level::text::user_status_enum
    ''')

    # Восстанавливаем старый тип Enum для `verification_level`
    old_seat_access_level_enum = postgresql.ENUM('GUEST', 'STUDENT', 'ADMIN', name='seataccesslevel')
    old_seat_access_level_enum.create(op.get_bind())

    op.execute('''
        ALTER TABLE users
        ALTER COLUMN verification_level
        TYPE seataccesslevel
        USING verification_level::text::seataccesslevel
    ''')

    # Удаляем новые типы Enum
    op.execute("DROP TYPE IF EXISTS useraccesslevel")
    op.execute("DROP TYPE IF EXISTS seataccesslevel")