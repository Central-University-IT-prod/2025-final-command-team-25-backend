from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncConnection
from config import config
from models import Base

engine = create_async_engine(
    config.DB_URI.replace("postgresql://", "postgresql+asyncpg://"),
)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_db_connection() -> AsyncConnection:
    async with engine.connect() as conn:
        yield conn
