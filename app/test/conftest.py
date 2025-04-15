import asyncio
import os

from fastapi import HTTPException, Request
from fastapi.security import APIKeyHeader
import jwt
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from config import config
from models import UserModel

import test_buffer
from db import get_db, get_db_connection
from main import app
import test_buffer
from service import authorize

def apply_alembic_migrations(alembic_path: str, db_uri: str, revision: str = "head"):
    """
    Apply Alembic migrations.

    :param alembic_path: Path to the Alembic directory
    :param db_uri: Database URI
    :param revision: Target revision (default is "head")
    """
    alembic_ini_path = os.path.join(alembic_path, "alembic_tests.ini")
    print(alembic_ini_path)
    alembic_config = Config(alembic_ini_path)
    alembic_config.set_main_option("sqlalchemy.url", db_uri)
    alembic_config.set_main_option("script_location", alembic_path)
    alembic_config.set_section_option("tests", "tests", "1")

    command.upgrade(alembic_config, revision)


@pytest.fixture(scope="function")
def postgres_container():
    with PostgresContainer("postgres:latest") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="function")
async def db_engine(postgres_container):
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.username
    password = postgres_container.password

    engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}",
        echo=True
    )

    # async_session = async_sessionmaker(
    #     bind=engine, class_=AsyncSession, expire_on_commit=False
    # )

    test_buffer.uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}"
    print(f"postgresql+asyncpg://{user}:{password}@{host}:{port}")

    print("A")

    apply_alembic_migrations("migrations", f"postgresql+psycopg2://{user}:{password}@{host}:{port}")

    print("B")

    await asyncio.sleep(1)

    yield engine

    # async with async_session() as session:
    #     yield session




@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    async with async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def db_connection(db_engine):
    async with db_engine.connect() as connection:
        yield connection


# Фикстура для тестового клиента
@pytest_asyncio.fixture(scope="function")
async def test_client(db_session, db_connection):
    print("d")

    async def override_get_db():
        return db_session

    async def override_get_db_connection():
        return db_connection

    class CheckAPIAccess(APIKeyHeader):
        async def __call__(self, request: Request):
            print(request.headers)
            token = await super().__call__(request)
            if token is None:
                raise HTTPException(status_code=401, detail="missed gggvtoken")
            token = token.replace('Bearer ', '')
            try:
                token_payload = jwt.decode(token, config.TOKEN_SECRET_KEY, algorithms=["HS256"])
            except jwt.PyJWTError:
                raise HTTPException(status_code=401, detail="Invalid token")

            client_id = token_payload["client_id"]

            # async with db_session() as session:
            session = db_session
            query = select(UserModel).where(UserModel.client_id == client_id)
            result = await session.execute(query)
            result = result.scalar()
            if result is None:
                raise HTTPException(status_code=401, detail="Invalid token no such user")

            if result.is_banned:
                raise HTTPException(status_code=403, detail="User is blocked")

            return client_id
    authorize_mock = CheckAPIAccess(name="Authorization", auto_error=False)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_connection] = override_get_db_connection
    app.dependency_overrides[authorize] = authorize_mock

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client

    print("e")


# @pytest_asyncio.fixture(scope="function")
# async def test_client_connection(db_connection):
#     print("d")
#
#     async def override_get_db():
#         return db_connection
#
#     app.dependency_overrides[get_db] = override_get_db
#
#     async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
#         yield client
#
#     print("e")