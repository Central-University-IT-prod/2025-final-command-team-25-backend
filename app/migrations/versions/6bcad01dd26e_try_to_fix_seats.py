"""try to fix seats

Revision ID: 6bcad01dd26e
Revises: ca8a58969e4d
Create Date: 2025-03-03 04:08:33.914850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bcad01dd26e'
down_revision: Union[str, None] = 'ca8a58969e4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa

# Определение нового типа ENUM
table_name = 'seats'
column_name = 'seat_access_level'
old_enum_name = 'accesslevel' # Замените на имя вашего старого enum типа
new_enum_name = 'accesslevel'

old_options = ('GUEST', 'STUDENT', 'ADMIN') # Получите старые опции enum, если это необходимо. Если нет, оставьте None
new_options = ('GUEST', 'STANDART', 'PRO')

def upgrade():
    # 1. Создаем новый Enum тип
    new_type = sa.Enum(*new_options, name=new_enum_name)
    new_type.create(op.get_bind(), checkfirst=False)

    # 2. Временное поле (необходимо, так как нельзя напрямую изменить тип столбца)
    temp_column = column_name + '_temp'

    # 3. Создаем временный столбец с новым типом Enum
    op.add_column(table_name, sa.Column(temp_column, new_type, nullable=True))

    # 4. Заполняем временный столбец значением 'GUEST'
    op.execute(f"UPDATE {table_name} SET {temp_column} = 'GUEST'")

    # 5. Удаляем старый столбец
    op.drop_column(table_name, column_name)

    # 6. Переименовываем временный столбец в имя старого столбца
    op.alter_column(table_name, temp_column, new_column_name=column_name)

    # # 7. Переопределяем тип столбца (необходимо для корректной работы alembic)
    # op.alter_column(table_name, column_name, type_=new_type, existing_nullable=True, postgresql_using='seat_access_level::text::seat_access_level_enum')



def downgrade():
    # Восстановление старого типа Enum.  Это примерный вариант, т.к. без знания старого типа точно восстановить невозможно.
    # Вам потребуется скорректировать этот код в зависимости от ваших реальных нужд.

    # 1. Создаем временный столбец (аналогично upgrade)
    temp_column = column_name + '_temp'

    # 2. Создаем временный столбец с типом String (т.к. точный старый enum неизвестен)
    op.add_column(table_name, sa.Column(temp_column, sa.String(), nullable=True))

    # 3. Заполняем временный столбец данными из старого столбца
    op.execute(f"UPDATE {table_name} SET {temp_column} = {column_name}::text")  # Приводим enum к text

    # 4. Удаляем текущий столбец с новым enum
    op.drop_column(table_name, column_name)

    # 5. Переименовываем временный столбец
    op.alter_column(table_name, temp_column, new_column_name=column_name)

    # 6.  Внимание! Здесь вам нужно будет создать *реальный* старый enum тип и переопределить тип столбца!
    #    Пример (если старый enum был с именами 'OLD1', 'OLD2'):
    #
    # old_type = sa.Enum('OLD1', 'OLD2', name=old_enum_name)
    # old_type.create(op.get_bind(), checkfirst=False)
    # op.alter_column(table_name, column_name, type_=old_type, existing_nullable=True, postgresql_using='seat_access_level::text::enum1')

    # 7. Если у вас нет информации о старом типе, можно оставить столбец как String.

    # 8. Удаляем новый enum тип
    new_type = sa.Enum(*new_options, name=new_enum_name)
    new_type.drop(op.get_bind(), checkfirst=False)