from schemas import UserCreation, User, PassportData
from models import UserModel
from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from api.users.exceptions import UserNameUniqueException, UserEmailUniqueException, NoSuchUserException, \
    NoAccessException
from api.admins.admin_access import check_access
from schemas.enums import SeatAccessLevel

from bcrypt import hashpw, gensalt
from uuid import UUID


async def create_user(creating_data: UserCreation, db: AsyncSession) -> User:
    query = select(UserModel).where(
        or_(
            UserModel.email == creating_data.email
        )
    )
    user: UserModel | None = (await db.execute(query)).scalar()
    if user is not None:
        raise UserEmailUniqueException()

    user = UserModel(**creating_data.model_dump())
    user.password = hashpw(
        creating_data.password.encode("utf-8"), gensalt(rounds=12)
    ).decode("utf-8")
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def get_user(client_id: str, db: AsyncSession) -> User:
    query = select(UserModel).where(UserModel.client_id == client_id)
    user = (await db.execute(query)).scalar()

    return user


async def add_passport(client_id: UUID, passport_data: PassportData, db: AsyncSession):
    stmt = update(UserModel).where(UserModel.client_id == client_id).values(
        passport_series=passport_data.series,
        verification_level='STANDARD',
        passport_number=passport_data.number,
        passport_name=passport_data.name
    )
    await db.execute(stmt)
    await db.commit()
