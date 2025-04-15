"""changed credentials for users

Revision ID: ea9a945b8bd2
Revises: b1e68f8f0405
Create Date: 2025-03-02 22:06:25.872448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'ea9a945b8bd2'
down_revision: Union[str, None] = 'b1e68f8f0405'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


users_data = [
    {
        "client_id": uuid.uuid4(),
        "username": "student",
        "email": "student@example.com",
        "access_level": "STUDENT",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "admin",
        "email": "admin@example.com",
        "access_level": "ADMIN",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    },
    {
        "client_id": uuid.uuid4(),
        "username": "guest",
        "email": "guest@example.com",
        "access_level": "GUEST",
        "password": "$2b$12$TzZWyUlHGoYsqdTPaY..o./Sfeo7J9aqlkZfl.SCOaQqO96bT1kHC", # Adminnn15)!
    }
]


def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            "users",
            sa.column("client_id", sa.UUID),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("access_level", sa.String),
            sa.column("password", sa.String),
        ),
        users_data
    )



def downgrade() -> None:
    pass
