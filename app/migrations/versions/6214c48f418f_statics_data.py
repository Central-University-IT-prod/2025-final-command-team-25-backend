"""statics_data

Revision ID: 6214c48f418f
Revises: 92a717ba60b1
Create Date: 2025-03-01 15:26:16.232646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6214c48f418f'
down_revision: Union[str, None] = '92a717ba60b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from schemas.enums import SeatAccessLevel  # Импортируем Enum, если он определён в models

# Статические данные для таблицы coworkings
coworkings_data = [
    {
        "coworking_id": uuid.uuid4(),
        "title": "Coworking A",
        "address": "Address A",
    },
    {
        "coworking_id": uuid.uuid4(),
        "title": "Coworking B",
        "address": "Address B",
    },
]

# Статические данные для таблицы seats
seats_data = [
    {
        "seat_id": uuid.uuid4(),
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworkings_data[0]["coworking_id"],  # Ссылка на первый coworking
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 10.5,
        "pos_y": 20.3,
    },
    {
        "seat_id": uuid.uuid4(),
        "seat_uuid": uuid.uuid4(),
        "coworking_id": coworkings_data[1]["coworking_id"],  # Ссылка на второй coworking
        "seat_access_level": SeatAccessLevel.GUEST,
        "pos_x": 15.7,
        "pos_y": 25.8,
    },
]

clients_data = [
    {
        "client_id": uuid.uuid4(),
        "username": "Admin1",
        "email": "Adminn1@example.com",
        "access_level": "ADMIN",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC",
    }
]

def upgrade():
    pass
    # Вставляем данные в таблицу coworkings
    # op.bulk_insert(
    #     sa.table(
    #         "coworkings",
    #         sa.Column("coworking_id", UUID(as_uuid=True)),
    #         sa.Column("title", sa.String),
    #     ),
    #     coworkings_data,
    # )

    # # Вставляем данные в таблицу seats
    # op.bulk_insert(
    #     sa.table(
    #         "seats",
    #         sa.Column("seat_id", UUID(as_uuid=True)),
    #         sa.Column("coworking_id", UUID(as_uuid=True)),
    #         sa.Column("seat_access_level", sa.Enum(SeatAccessLevel)),
    #         sa.Column("pos_x", sa.Float),
    #         sa.Column("pos_y", sa.Float),
    #     ),
    #     seats_data,
    # )

    # op.bulk_insert(
    #     sa.table(
    #         "users",
    #         sa.Column("client_id", UUID(as_uuid=True)),
    #         sa.Column("username", sa.String),
    #         sa.Column("email", sa.String),
    #         sa.Column("access_level", sa.Enum(SeatAccessLevel)),
    #         sa.Column("password", sa.String),
    #     ),
    #     clients_data,
    # )

def downgrade():
    # # Удаляем данные из таблицы seats
    # op.execute("DELETE FROM seats")

    # # Удаляем данные из таблицы coworkings
    # op.execute("DELETE FROM coworkings")

    # # Удаляем данные из таблицы coworkings
    # op.execute("DELETE FROM users")
    pass