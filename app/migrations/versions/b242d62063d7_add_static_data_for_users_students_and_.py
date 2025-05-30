"""add static data for users (students and admins)

Revision ID: b242d62063d7
Revises: 78c949fdf1e8
Create Date: 2025-03-03 21:47:24.394232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision: str = 'b242d62063d7'
down_revision: Union[str, None] = '78c949fdf1e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


users_data = [
    {
        "client_id": uuid.uuid4(),
        "username": "student",
        "email": "student1@example.com",
        "access_level": "STUDENT",
        "verification_level": "PRO",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "student",
        "email": "student2@example.com",
        "verification_level": "PRO",
        "access_level": "STUDENT",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "admin",
        "email": "admin1@example.com",
        "verification_level": "PRO",
        "access_level": "ADMIN",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "admin",
        "email": "admin2@example.com",
        "verification_level": "PRO",
        "access_level": "ADMIN",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    }
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
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
        users_data
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    ...
    # ### end Alembic commands ###
