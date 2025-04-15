"""add statics data for seats

Revision ID: b1e68f8f0405
Revises: 88422c34f0f8
Create Date: 2025-03-02 21:05:35.872453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1e68f8f0405'
down_revision: Union[str, None] = '88422c34f0f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from schemas.enums import SeatAccessLevel  # Импортируйте ваш Enum


coworking_id = uuid.uuid4()

new_coworking_data = [{
    "coworking_id": coworking_id,  # Генерируем UUID для новой записи
    "title": "Example Coworking",
    "address": "123 Main St, City, Country",
    "tz_offset": 3,  # Пример смещения часового пояса
}]

# Статические данные для стульев
static_seats_data = [
    {
        "seat_id": "1",
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworking_id,  # Замените на реальный coworking_id
        "seat_access_level": SeatAccessLevel.GUEST,  # Уровень доступа
        "pos_x": 10.0,
        "pos_y": 200.0,
    },
    {
        "seat_id": "2",
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworking_id,  # Замените на реальный coworking_id
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 60.0,
        "pos_y": 200.0,
    },
    {
        "seat_id": "3",
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworking_id,  # Замените на реальный coworking_id
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 110.0,
        "pos_y": 200.0,
    },
    {
        "seat_id": "4",
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworking_id,  # Замените на реальный coworking_id
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 160.0,
        "pos_y": 200.0,
    },
    {
        "seat_id": "5",
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworking_id,  # Замените на реальный coworking_id
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 210.0,
        "pos_y": 200.0,
    },
]

def upgrade():
    op.execute("DELETE FROM seat_bookings")
    op.execute("DELETE FROM bookings")
    op.execute("DELETE FROM seats CASCADE")
    op.execute("DELETE FROM coworkings CASCADE")

    
    op.bulk_insert(
        sa.table(
            "coworkings",
            sa.Column("coworking_id", sa.UUID()),
            sa.Column("title", sa.String()),
            sa.Column("address", sa.String()),
            sa.Column("tz_offset", sa.Integer()),
        ),
        new_coworking_data,
    )

    op.bulk_insert(
        sa.table(
            "seats",
            sa.Column("seat_id", sa.String()),
            sa.Column("seat_uuid", sa.UUID()),
            sa.Column("coworking_id", sa.UUID()),
            sa.Column("seat_access_level", sa.Enum(SeatAccessLevel)),
            sa.Column("pos_x", sa.Float()),
            sa.Column("pos_y", sa.Float()),
        ),
        static_seats_data,
    )

def downgrade():
    # Удаляем статические данные из таблицы seats
    for seat_data in static_seats_data:
        op.execute(
            f"""
            DELETE FROM seats
            WHERE seat_id = '{seat_data["seat_id"]}';
            """
        )