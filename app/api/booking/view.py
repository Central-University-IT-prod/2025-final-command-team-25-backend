from fastapi import APIRouter, Query, Response, status, Path
from .crud import (
    get_all_seats, 
    book_seat, 
    change_book_seat, 
    delete_book_seat, 
    my_bookings,
    get_taken_times,
    accept_invite
)
from uuid import UUID
from typing import Annotated
from datetime import date
from dependencies import session, Auth, connection
from schemas import FreeSeatsFilter, RegisterBook, BookingChange, SeatFree, BookingObject, TimeSlot, Invitation, \
    InvitationInfo

router = APIRouter(prefix="/booking", tags=["booking"])




@router.post(
    "/seat",
    response_model=BookingObject
)
async def book_seat_handler(
    booking_data: RegisterBook, user_id: Auth, db: connection
):
    booking = await book_seat(booking_data, user_id, db)
    return booking


@router.delete(
    "/{booking_id}",
    status_code=204
)
async def delete_book_seat_handler(
    booking_id: str, 
    user_id: Auth, 
    db: session
) -> None:
    
    await delete_book_seat(booking_id, user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '/seat/occupied',
    response_model=list[TimeSlot]
)
async def taken_seat_times_handler(
    db: session,
    _: Auth,
    seat_uuids: list[UUID] = Query(..., min_length=1, description="Места, для которых необходимо найти свободное время"),
    days: list[date] = Query(..., min_length=1, description="Дни, на которые необходимо найти свободное время"),
):
    slots = await get_taken_times(seat_uuids, days, db)
    return slots


@router.patch(
    "/seat/{booking_id}",
    response_model=BookingObject
)
async def change_book_seat_handler(
    booking_data: BookingChange, user_id: Auth, db: session, booking_id: str
) -> BookingObject:
    
    booking = await change_book_seat(booking_data, booking_id, user_id, db)
    return booking


@router.get(
    "/my/{coworking_id}",
    response_model=list[BookingObject]
)
async def get_my_bookings_handler(
    user_id: Auth, 
    db: session,
    coworking_id: Annotated[UUID, Path(..., description='uuid коворкинга')]
) -> list[BookingObject]:
    
    bookings = await my_bookings(user_id, coworking_id, db)
    return bookings

@router.post(
    "/invite",
    response_model=InvitationInfo
)
async def accept_invite_handler(
    user_id: Auth,
    invite: Invitation,
    db: session
):
    invitation_info = await accept_invite(user_id, invite, db)
    return invitation_info


@router.get(
    "/{coworking_id}/free_seats",
    response_model=list[SeatFree]
)
async def get_free_seats_handler(
    db: session,
    user_id: Auth,
    coworking_id: Annotated[UUID, Path(..., description='uuid коворкинга')],
    filter_params: FreeSeatsFilter = Query(None),
) -> list[SeatFree]:
    
    seats = await get_all_seats(coworking_id, filter_params, user_id, db)
    return seats