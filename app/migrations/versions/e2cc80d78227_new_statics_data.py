"""new statics data

Revision ID: e2cc80d78227
Revises: 70db0a9f53bd
Create Date: 2025-03-02 00:48:01.922679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2cc80d78227'
down_revision: Union[str, None] = '70db0a9f53bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
from alembic import op
import sqlalchemy as sa
import uuid

# Импортируем модели, если нужно (для типов и проверок)
from models import SeatsModel, CoworkingModel

coworking_id = uuid.uuid4()
coworking_id_2 = uuid.uuid4()

# Статические данные для таблицы coworkings
coworkings_data = [
    {
        "coworking_id": coworking_id,
        "title": "Coworking Space 1",
        "address": "123 Main St, City, Country",
    },
    {
        "coworking_id": coworking_id_2,
        "title": "Coworking Space 2",
        "address": "456 Elm St, City, Country",
    },
]

seat_uuid_1 = uuid.uuid4()

 # Статические данные для таблицы seats
seats_data = [
    {
        "seat_uuid": seat_uuid_1,
        "seat_id": 1,
        "coworking_id": coworking_id,  # Используем первый coworking_id
        "seat_access_level": "GUEST",
        "pos_x": 10.5,
        "pos_y": 15.3,
    },
    {
        "seat_uuid": uuid.uuid4(),
        "seat_id": 2,
        "coworking_id": coworking_id, 
        "seat_access_level": "GUEST",
        "pos_x": 20.7,
        "pos_y": 25.1,
    },
    {
        "seat_uuid": uuid.uuid4(),
        "seat_id": 3,
        "coworking_id": coworking_id,  # Используем первый coworking_id
        "seat_access_level": "GUEST",
        "pos_x": 10.5,
        "pos_y": 15.3,
    },
    {
        "seat_uuid": uuid.uuid4(),
        "seat_id": 4,
        "coworking_id": coworking_id, 
        "seat_access_level": "STUDENT",
        "pos_x": 20.7,
        "pos_y": 25.1,
    },
    {
        "seat_uuid": uuid.uuid4(),
        "seat_id": 5,
        "coworking_id": coworking_id, 
        "seat_access_level": "STUDENT",
        "pos_x": 20.7,
        "pos_y": 25.1,
    },
]

user_id_1 = uuid.uuid4()

users_data = [
    {
        "client_id": user_id_1,
        "username": "student",
        "email": "Hxk4w@example.com",
        "access_level": "STUDENT",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "admin",
        "email": "Adminn1@example.com",
        "access_level": "ADMIN",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    }
]

booking_id_1 = uuid.uuid4()

bookings_data = [
    {
        "booking_id": booking_id_1,
        "user_id": user_id_1,
        "start_date": "2023-05-01 10:00:00",
        "end_date": "2023-05-01 11:00:00",
    }
]

bookings_seats = [
    {
        "booking_id": booking_id_1,
        "seat_uuid": seat_uuid_1,
    }
]

def upgrade():
    # Вставляем данные в таблицу coworkings
    op.bulk_insert(
        sa.table(
            "coworkings",
            sa.Column("coworking_id", sa.UUID()),
            sa.Column("title", sa.String()),
            sa.Column("address", sa.String()),
        ),
        coworkings_data,
    )

    # Вставляем данные в таблицу seats
    op.bulk_insert(
        sa.table(
            "seats",
            sa.Column("seat_uuid", sa.UUID()),
            sa.Column("seat_id", sa.Integer()),
            sa.Column("coworking_id", sa.UUID()),
            sa.Column("seat_access_level", sa.String()),
            sa.Column("pos_x", sa.Float()),
            sa.Column("pos_y", sa.Float()),
        ),
        seats_data,
    )

    # Вставляем данные в таблицу users
    op.bulk_insert(
        sa.table(
            "users",
            sa.Column("client_id", sa.UUID()),
            sa.Column("username", sa.String()),
            sa.Column("email", sa.String()),
            sa.Column("access_level", sa.String()),
            sa.Column("password", sa.String()),
        ),
        users_data,
    )
    op.bulk_insert(
        sa.table(
            "bookings",
            sa.Column("booking_id", sa.UUID()),
            sa.Column("user_id", sa.UUID()),
            sa.Column("start_date", sa.DateTime()),
            sa.Column("end_date", sa.DateTime()),
        ),
        bookings_data
    )

    op.bulk_insert(
        sa.table(
            "seat_bookings",
            sa.Column("booking_id", sa.UUID()),
            sa.Column("seat_uuid", sa.Integer()),
        ),
        bookings_seats,
    )

def downgrade():
    # Удаляем статические данные из таблиц
    op.execute("DELETE FROM seats WHERE seat_uuid IN (SELECT seat_uuid FROM seats LIMIT 2)")
    op.execute("DELETE FROM coworkings WHERE coworking_id IN (SELECT coworking_id FROM coworkings LIMIT 2)")
    op.execute("DELETE FROM users WHERE client_id IN (SELECT client_id FROM users LIMIT 2)")