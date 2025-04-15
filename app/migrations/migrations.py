# noinspection PyUnresolvedReferences
from sqlalchemy import create_engine, pool

from alembic import context
from models import Base

target_metadata = Base.metadata

config = context.config

def make_migration(db_uri):
    print(db_uri)

    connectable = create_engine(
        db_uri,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        print(context)

        with context.begin_transaction():
            context.run_migrations()
