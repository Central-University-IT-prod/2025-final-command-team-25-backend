from datetime import timedelta, date, datetime, timezone
from typing import Any
from uuid import uuid4, UUID

from sqlalchemy import select, and_, case, literal, update, text, insert, join, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from sqlalchemy.orm import selectinload, joinedload

from api.admins.admin_access import check_access
from models import BookingModel, SeatsModel, SeatBookingModel, UserModel, CoworkingModel
from models.booking import SeatBooking, Booking
from schemas import FreeSeatsFilter, RegisterBook, BookingChange, RequiredLevel, UserAccessLevel, \
    Invitation, InvitationInfo
from .exceptions import SeatAlreadyBookedException, NoSuchBookingException, CoworkingNotFound, NoAccessException, \
    DateValidationException, InvitationExpiredException


async def get_all_seats(
        coworking_id: UUID,
        filter_params: FreeSeatsFilter,
        client_id,
        db: AsyncSession
) -> list[dict]:
    coworking = await db.get(CoworkingModel, coworking_id)
    if coworking is None:
        raise CoworkingNotFound()

    # Получаем уровни для пользователя
    user_verification = await db.scalar(
        select(UserModel.verification_level).where(UserModel.client_id == client_id)
    )

    user_access_level = await db.scalar(
        select(UserModel.access_level).where(UserModel.client_id == client_id)
    )

    # Построим подзапрос для определения занятых мест
    occupied_subq = (
        select(SeatBooking.seat_uuid)
        .select_from(SeatBooking)
        .join(BookingModel)
        .join(SeatsModel)
        .where(
            BookingModel.end_date > filter_params.start_date,
            BookingModel.start_date < filter_params.end_date,
            SeatsModel.coworking_id == coworking_id
        )
    )

    is_free_expr = case(
        (SeatsModel.seat_uuid.in_(occupied_subq), literal(False)),
        else_=literal(True)
    ).label("is_free")

    query = (
        select(
            SeatsModel.seat_uuid,
            SeatsModel.seat_id,
            SeatsModel.seat_access_level,
            SeatsModel.seat_type,
            SeatsModel.pos_x,
            SeatsModel.pos_y,
            SeatsModel.width,
            SeatsModel.height,
            SeatsModel.rx,
            SeatsModel.rotation,
            SeatsModel.price,
            is_free_expr
        )
        .where(SeatsModel.coworking_id == coworking_id)
    )

    result = await db.execute(query)
    rows = result.mappings().all()

    print(rows)
    levels = {
        'GUEST': 0,
        'STANDARD': 1,
        'PRO': 2
    }

    processed_rows = []
    for row in rows:
        seat_level = row["seat_access_level"]  # Это экземпляр SeatAccessLevel
        if user_access_level == UserAccessLevel.STUDENT:
            req_level = RequiredLevel.AVAILABLE.value
        else:
            req_level = (RequiredLevel.AVAILABLE.value
                         if levels[seat_level.value] <= levels[user_verification.value]
                         else seat_level.value)
        new_row = dict(row)
        new_row["required_level"] = req_level
        print(new_row)
        processed_rows.append(new_row)

    # Если нужна сортировка, можно отсортировать processed_rows здесь (по требованию)
    return processed_rows


async def fetch_booking_with_seats(db: AsyncConnection, booking_id: UUID, user_id) -> dict[str, Any] | None:
    # Query to join Booking and SeatBooking tables

    print("Booking with seats: ", booking_id)

    result = await db.execute(
        select(
            BookingModel.booking_id,
            BookingModel.start_date,
            BookingModel.end_date,
            SeatBookingModel.seat_id,
            SeatBookingModel.seat_uuid,
            SeatBookingModel.user_id
        )
        .select_from(
            join(
                BookingModel,
                SeatBookingModel,
                BookingModel.booking_id == SeatBookingModel.booking_id,
                isouter=True  # So it works even if there are no seats
            )
        )
        .where(BookingModel.booking_id == booking_id)
    )

    rows = result.fetchall()

    if rows is None:
        return None

    # Initialize the booking object with basic info
    first_row = rows[0]
    booking_data = {
        "booking_id": str(first_row.booking_id),
        "user_id": str(first_row.user_id),
        "start_date": first_row.start_date.isoformat(),
        "end_date": first_row.end_date.isoformat(),
        "seats": []
    }

    # Collect seats (some rows might have NULL seats if outer join matched no seats)
    for row in rows:
        if row.seat_id is not None:
            booking_data["seats"].append({
                "seat_id": row.seat_id,
                "seat_uuid": str(row.seat_uuid),
                "is_owner": str(row.user_id) == str(user_id)
            })
    if len(booking_data["seats"]) > 1:
        booking_data[
            'invite_url'] = f'https://prod-team-25-7si7srok.REDACTED/static/pages/invite_redirect.html?booking_id={str(first_row.booking_id)}'

    return booking_data


async def book_seat(booking_data: RegisterBook, user_id: UUID, db: AsyncConnection):
    async with db.begin():

        # Set transaction isolation level
        await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))

        booking_id = uuid4()
        query = (
            select(CoworkingModel.tz_offset)
            .join(SeatsModel, SeatsModel.coworking_id == CoworkingModel.coworking_id)
            .where(SeatsModel.seat_uuid == booking_data.seats[0].seat_uuid)
        )

        result = await db.execute(query)
        tz_offset = result.scalar()

        now = datetime.now() if booking_data.start_date.tzinfo is None else datetime.now().astimezone(timezone.utc)

        print("------------ TIME ZONE -------------")
        print(booking_data.start_date.tzinfo)
        print(now + timedelta(hours=tz_offset) + timedelta(minutes=1))
        print("------------ END -------------")

        if booking_data.start_date < now + timedelta(hours=tz_offset) + timedelta(minutes=1):
            raise DateValidationException()

        # Check for conflicting bookings
        query = (
            select(SeatBookingModel)
            .join(BookingModel, SeatBookingModel.booking_id == BookingModel.booking_id)
            .where(
                and_(
                    BookingModel.start_date < booking_data.end_date,
                    BookingModel.end_date > booking_data.start_date,
                ),
                SeatBookingModel.seat_uuid.in_(list(map(lambda x: x.seat_uuid, booking_data.seats))),
            )
        )
        result = await db.execute(query)
        conflict = result.scalar()

        if conflict is not None:
            raise SeatAlreadyBookedException()

        # Insert booking into BookingModel table
        await db.execute(
            insert(BookingModel).values(
                booking_id=booking_id,
                user_id=user_id,
                start_date=booking_data.start_date,
                end_date=booking_data.end_date,
            )
        )

        # Insert seats into SeatBookingModel table
        seat_bookings = []
        for index, seat in enumerate(booking_data.seats):
            seat_bookings.append(
                {
                    "booking_id": booking_id,
                    "seat_uuid": seat.seat_uuid,
                    "seat_id": seat.seat_id,
                    "user_id": user_id if index == 0 else None
                }
            )

        if seat_bookings:
            await db.execute(
                insert(SeatBookingModel),
                seat_bookings
            )

        # Commit happens automatically on exiting async with block

        # After committing, query back the booking with its seats to return full data
        return await fetch_booking_with_seats(db, booking_id, user_id)


async def delete_book_seat(booking_id: UUID, user_id: UUID, db: AsyncSession):
    booking = await db.scalar(select(Booking).where(Booking.booking_id == booking_id))
    if booking is None:
        raise NoSuchBookingException()

    if not (await check_access(user_id, db)) and str(booking.user_id) != str(user_id):
        raise NoAccessException()

    await db.delete(booking)
    await db.commit()


class TimeSlot:
    def __init__(self, time: datetime, slot_type: str):
        self.time = time
        self.slot_type = slot_type

    def to_dict(self):
        return {
            "time": self.time.isoformat(),
            "slot_type": self.slot_type
        }


async def get_taken_times(
        seat_uuids: list[UUID],
        target_dates: list[date],
        session: AsyncSession
) -> list[dict]:
    date = target_dates[0]
    seat_uuid = seat_uuids[0]
    start_of_day = datetime(date.year, date.month, date.day, 0, 0, tzinfo=timezone.utc)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, tzinfo=timezone.utc)

    # Fetch all bookings for this seat on the given date
    query = (
        select(Booking)
        .join(SeatBooking, Booking.booking_id == SeatBooking.booking_id)
        .where(
            SeatBooking.seat_uuid == seat_uuid,
            Booking.start_date <= end_of_day,
            Booking.end_date >= start_of_day
        )
        .options(joinedload(Booking.seats))
    )

    result = await session.execute(query)
    bookings = list(result.scalars().unique())

    # 1. Merge overlapping/adjacent bookings into continuous blocks
    merged_bookings = []
    if bookings:
        # Sort by start date
        bookings.sort(key=lambda b: b.start_date)

        # Initialize the first merged block
        current_start = bookings[0].start_date
        current_end = bookings[0].end_date

        for booking in bookings[1:]:
            if booking.start_date <= current_end:  # Overlapping or adjacent
                # Extend current block
                current_end = max(current_end, booking.end_date)
            else:
                # Save the previous block and start a new one
                merged_bookings.append((current_start, current_end))
                current_start = booking.start_date
                current_end = booking.end_date

        # Don't forget to append the last block
        merged_bookings.append((current_start, current_end))

    # 2. Generate all 30-minute slots for the day
    slots = []
    current_time = start_of_day
    while current_time <= end_of_day:
        slots.append({
            "time": current_time.isoformat(),
            "slot_type": None  # Will be determined below
        })
        current_time += timedelta(minutes=30)

    # 3. Assign slot types based on merged bookings
    for slot in slots:
        slot_time = datetime.fromisoformat(slot["time"]).astimezone(timezone.utc)

        for start, end in merged_bookings:
            if start <= slot_time < end:
                slot["slot_type"] = "INTERMEDIATE"

            # Only mark BOUNDARY if it's the first or last slot in a merged range
            if slot_time == start or slot_time == end:
                slot["slot_type"] = "BOUNDARY"

    # 4. Filter and return only occupied slots
    return [slot for slot in slots if slot["slot_type"] is not None]


async def change_book_seat(booking_data: BookingChange, booking_id: str, user_id: UUID, db: AsyncSession):
    query = (
        select(CoworkingModel.tz_offset)
        .join(SeatsModel, SeatsModel.coworking_id == CoworkingModel.coworking_id)
        .join(SeatBooking, SeatBooking.seat_uuid == SeatsModel.seat_uuid)
        .where(SeatBooking.booking_id == booking_id)
    )
    result = await db.execute(query)
    tz_offset = result.scalar()

    now = datetime.now().astimezone(timezone.utc) if booking_data.start_date.tzinfo is not None else datetime.now()

    print("------------ TIME ZONES 3 ------------")
    print(now, now.tzinfo, "(TZ INFO NOW)")
    print(booking_data.start_date, booking_data.start_date.tzinfo, "(TZ INFO BOOKING DATA)")
    print(now + timedelta(hours=tz_offset) + timedelta(minutes=1), "(NOW + TZ OFFSET + 1 MINUTE)")
    print("------------ END -------------")

    if booking_data.start_date < now + timedelta(hours=tz_offset) + timedelta(minutes=1):
        raise DateValidationException()

    booking = await db.scalar(
        select(BookingModel)
        .where(BookingModel.booking_id == booking_id)
        .options(selectinload(BookingModel.seats))
    )
    if booking is None:
        raise NoSuchBookingException()

    if not (await check_access(user_id, db)) and str(booking.user_id) != str(user_id):
        raise NoAccessException()

    stmt = (
        update(BookingModel)
        .where(BookingModel.booking_id == booking_id)
        .values(**booking_data.model_dump())
    )

    print(stmt)
    print(stmt.compile())
    print((await db.execute(stmt)))
    await db.commit()
    await db.refresh(booking)
    return await fetch_booking_with_seats(db, booking_id, user_id)


async def my_bookings(client_id: UUID, coworking_id: UUID, db: AsyncSession) -> list[dict]:
    query = (
        select(BookingModel)
        .join(SeatBookingModel, SeatBookingModel.booking_id == BookingModel.booking_id, isouter=True)
        .where(
            or_(
                BookingModel.user_id == client_id,
                SeatBookingModel.user_id == client_id
            )
        )
        .options(selectinload(BookingModel.seats))
        .distinct(BookingModel.booking_id)  # <-- distinct works here correctly
    )

    bookings_list = (await db.scalars(query)).all()

    result = []
    for booking in bookings_list:
        seats_list = []
        for seat_booking in booking.seats:
            seat_data = {
                "seat_id": seat_booking.seat_id,
                "seat_uuid": seat_booking.seat_uuid,
                "is_owner": (str(seat_booking.user_id) == str(client_id))
            }
            seats_list.append(seat_data)
        booking_data = {
            "booking_id": booking.booking_id,
            "user_id": booking.user_id,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "seats": seats_list,
            "invite_url": f'https://prod-team-25-7si7srok.REDACTED/static/pages/invite_redirect.html?booking_id={str(booking.booking_id).replace("-", "_")}' if len(
                seats_list) > 1 else None
        }
        result.append(booking_data)

    return result


async def accept_invite(
        user_id: UUID,
        invite: Invitation,
        db: AsyncSession
):
    booking = await db.scalar(
        select(BookingModel)
        .where(BookingModel.booking_id == invite.booking_id)
        .options(selectinload(BookingModel.seats))
        .options(selectinload(BookingModel.user))
    )

    if booking is None:
        raise NoSuchBookingException()

    for seat_booking in booking.seats:
        if seat_booking.user_id == user_id:
            raise InvitationExpiredException()

    seat_booking_seat_id = None
    seat_booking_booking_id = None
    for seat_booking in booking.seats:
        if seat_booking.user_id is None:
            seat_booking_seat_id = seat_booking.seat_uuid
            seat_booking_booking_id = seat_booking.booking_id

            break
    else:
        raise InvitationExpiredException()

    await db.execute(text("UPDATE seat_bookings SET user_id = :user_id WHERE seat_uuid = :seat_uuid AND booking_id = :booking_id"), {
        "user_id": user_id,
        "seat_uuid": seat_booking_seat_id,
        "booking_id": seat_booking_booking_id
    })
        
    await db.commit()

    return InvitationInfo(
        booker=booking.user,
        seat=seat_booking
    )
