from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models import UserModel
from models.users import UserAccessLevel


async def check_access(user_id, db: AsyncSession) -> bool:
    query = select(UserModel).where(
        and_(
            UserModel.client_id == user_id,
            UserModel.access_level == UserAccessLevel.ADMIN.value,
        )
    )
    user = (await db.execute(query)).scalar()

    return user is not None
