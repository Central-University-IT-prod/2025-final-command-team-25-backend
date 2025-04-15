import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_check_db(db_session):
    async with db_session as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1, "База данных не вернула ожидаемый результат"
        result = await session.execute(text("SELECT * FROM users"))
        print(result.scalars())
        print(result.fetchall())
