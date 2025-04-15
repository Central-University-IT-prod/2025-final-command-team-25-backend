import json
from sqlalchemy.ext.asyncio import AsyncSession
from models import BookingModel, SeatBookingModel, UserModel
from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone
from schemas import User, QRPayload, QRResponse
from .exceptions import WrongQRException, BookingNotFoundException, NoSuchUserException
from schemas.enums import SeatAccessLevel
from models import SeatsModel


async def get_all_bookings(db: AsyncSession) -> list[BookingModel]:
    bookings = await db.scalars(
        select(BookingModel)
        .options(
            selectinload(BookingModel.seats),
            selectinload(BookingModel.user)
        )
    )
    return bookings.all()


async def get_all_clients(db: AsyncSession) -> list[str]:
    query = select(UserModel)

    clients: list[dict] = (await db.execute(query)).scalars().all()

    return list(map(lambda x: User(client_id = x.client_id, username = x.username, email = x.email, access_level = x.access_level), clients))


async def get_client_bookings(client_id: UUID, db: AsyncSession):
    bookings = await db.scalars(
        select(BookingModel)
        .options(selectinload(BookingModel.seats))
        .where(BookingModel.user_id == client_id)
    )
    return bookings.all()


async def delete_user(
    client_id: UUID, 
    db: AsyncSession
) -> None:
    
    user = await db.scalar(
        select(UserModel)
        .where(UserModel.client_id == client_id)
    )
    if user is None:
        return

    await db.execute(text("DELETE FROM seat_bookings WHERE user_id = :client_id"), {"client_id": client_id})

    await db.delete(user)
    await db.commit()


async def check_qr(
    qr_data_str: str, 
    db: AsyncSession
) -> QRResponse:
    try:
        data = json.loads(qr_data_str)
    except json.JSONDecodeError:
        raise WrongQRException()
    
    try:
        payload = QRPayload(**data)
    except Exception as e:
        raise WrongQRException()
    
    stmt = (
        select(BookingModel)
        .options(
            selectinload(BookingModel.seats).selectinload(SeatBookingModel.seat),
            selectinload(BookingModel.user)
        )
        .where(BookingModel.booking_id == payload.booking_id)
    )
    result = await db.execute(stmt)
    booking = result.scalar()
    if booking is None:
        raise BookingNotFoundException()
    
    for seat_booking in booking.seats:
        if seat_booking.seat_uuid == payload.seat_uuid:
            break
    else:
        raise BookingNotFoundException()
    
    need_verification = (seat_booking.seat.seat_access_level.value != booking.user.verification_level.value)
    current_time = datetime.now(timezone.utc)
    accept = booking.start_date <= current_time <= booking.end_date

    query = (
        select(SeatsModel)
        .where(
            SeatsModel.seat_uuid == payload.seat_uuid
        )
    )
    seat = (await db.execute(query)).scalar()

    return QRResponse(
        booking_id=booking.booking_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        seat=seat,
        user=booking.user,
        need_verification=need_verification,
        accept=accept
    )


# async def change_user(
#     client_id: UUID, 
#     user_update: UserUpdate, 
#     db: AsyncSession
# ) -> UserModel:
    
#     stmt = select(UserModel).where(UserModel.client_id == client_id)
#     user_instance = (await db.execute(stmt)).scalar_one_or_none()
#     if user_instance is None:
#         raise NoSuchUserException()
    
#     update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
#     for field, value in update_data.items():
#         setattr(user_instance, field, value)
    
#     await db.commit()
#     await db.refresh(user_instance)
    
#     return user_instance


async def ban_user(client_id: UUID, db: AsyncSession):
    user = await db.scalar(select(UserModel).where(UserModel.client_id == client_id))
    if user is None:
        raise NoSuchUserException()
    
    stmt = update(UserModel).where(UserModel.client_id == client_id).values(is_banned = True)
    await db.execute(stmt)
    stmt = delete(BookingModel).where(BookingModel.user_id == client_id)
    await db.execute(stmt)
    await db.commit()


async def increase_verification(client_id: UUID, db: AsyncSession):
    user = await db.scalar(select(UserModel).where(UserModel.client_id == client_id))
    if user is None:
        raise NoSuchUserException()
    
    stmt = update(UserModel).where(UserModel.client_id == client_id).values(verification_level = SeatAccessLevel.PRO)
    await db.execute(stmt)
    await db.commit()