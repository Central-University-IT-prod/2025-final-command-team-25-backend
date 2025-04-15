"""Clean

Revision ID: 26daa637b8ab
Revises: 9b971ade50d5
Create Date: 2025-03-04 08:48:54.438514

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '26daa637b8ab'
down_revision: Union[str, None] = '9b971ade50d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM seat_bookings")
    op.execute("DELETE FROM bookings")
    op.execute("DELETE FROM users")

    admins = [
        {
            "client_id": uuid4(),
            'username': 'admin1',
            'email': 'admin@example.com',
            'password': 'adminadmin',
            'access_level': 'ADMIN',
            'verification_level': 'PRO'
        },
        {
            "client_id": uuid4(),
            'username': 'admin2',
            'email': 'admin2@example.com',
            'password': 'adminadmin',
            'access_level': 'ADMIN',
            'verification_level': 'PRO'
        },
        {
            "client_id": uuid4(),
            'username': 'admin2',
            'email': 'admin1@example.com',
            'password': 'adminadmin',
            'access_level': 'ADMIN',
            'verification_level': 'PRO'
        }
    ]

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("client_id", sa.UUID),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("access_level", sa.String),
            sa.column("verification_level", sa.String),
            sa.column("password", sa.String),
        ),
        admins
    )

    students = [
        {
            "client_id": uuid4(),
            'username': 'student1',
            'email': 'student@example.com',
            'password': 'studentstudent',
            'access_level': 'STUDENT',
            'verification_level': 'PRO'
        },
        {
            "client_id": uuid4(),
            'username': 'student2',
            'email': 'student1@example.com',
            'password': 'studentstudent',
            'access_level': 'STUDENT',
            'verification_level': 'PRO'
        },
        {
            "client_id": uuid4(),
            'username': 'student3',
            'email': 'student2@example.com',
            'password': 'studentstudent',
            'access_level': 'STUDENT',
            'verification_level': 'PRO'
        }
    ]
    op.bulk_insert(
        sa.table(
            "users",
            sa.column("client_id", sa.UUID),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("access_level", sa.String),
            sa.column("verification_level", sa.String),
            sa.column("password", sa.String),
        ),
        students
    )

    guests = [
        {
            "client_id": uuid4(),
            'username': 'guest',
            'email': 'guest@example.com',
            'password': 'guestguest',
            'access_level': 'GUEST',
            'verification_level': 'GUEST'
        },
        {
            "client_id": uuid4(),
            'username': 'guest',
            'email': 'guest1@example.com',
            'password': 'guestguest',
            'access_level': 'GUEST',
            'verification_level': 'GUEST'
        },
        {
            "client_id": uuid4(),
            'username': 'guest',
            'email': 'guest2@example.com',
            'password': 'guestguest',
            'access_level': 'GUEST',
            'verification_level': 'STANDARD'
        },
        {
            "client_id": uuid4(),
            'username': 'guest',
            'email': 'guest3@example.com',
            'password': 'guestguest',
            'access_level': 'GUEST',
            'verification_level': 'STANDARD'
        },
    ]

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("client_id", sa.UUID),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("access_level", sa.String),
            sa.column("verification_level", sa.String),
            sa.column("password", sa.String),
        ),
        guests
    )


def downgrade() -> None:
    pass
