from fastapi import APIRouter, Path, Response, status
from .crud import (
    get_all_bookings, 
    get_all_clients,
    get_client_bookings,
    delete_user,
    check_qr,
    # change_user,
    ban_user,
    increase_verification
)
from typing import Annotated
from uuid import UUID
from .admin_access import check_access
from dependencies import session, Auth
from schemas import User, BookingObjAdmin, BookingObject, QRData, QRResponse, PassportData
from .exceptions import NoAdminAccessException

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("/all_clients")
async def get_all_clients_handler(user_id: Auth, db: session) -> list[User]:
    if not await check_access(user_id, db):
        raise NoAdminAccessException()

    return await get_all_clients(db)


@router.get(
    "/bookings",
    response_model=list[BookingObjAdmin]
)
async def get_all_bookings_handler(
    db: session, 
    user_id: Auth
) -> list[BookingObjAdmin]:
    
    if not await check_access(user_id, db):
        raise NoAdminAccessException()

    return await get_all_bookings(db)

@router.get(
    "/bookings/{user_id}",
    response_model=list[BookingObject]
)
async def get_all_bookings_handler(
    client_id: Annotated[UUID, Path(..., alias='user_id')],
    user_id: Auth,
    db: session,  
) -> list[BookingObject]:
    if not await check_access(user_id, db):
        raise NoAdminAccessException()

    bookings = await get_client_bookings(client_id, db)
    return bookings


@router.delete(
    "/{user_id}",
    status_code=204
)
async def delete_user_handler(
    client_id: Annotated[UUID, Path(..., alias='user_id')],
    user_id: Auth,
    db: session,  
) -> None:
    if not await check_access(user_id, db):
        raise NoAdminAccessException()

    await delete_user(client_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/check_qr",
    response_model=QRResponse
)
async def check_qr_handler(
    qr_data: QRData,
    user_id: Auth, 
    db: session
) -> None:
    
    if not await check_access(user_id, db):
        raise NoAdminAccessException()
    
    qr_out = await check_qr(qr_data.qr_data, db)
    return qr_out

# @router.patch(
#     '/user/{client_id}',
#     response_model=User
# )
# async def change_user_handler(
#     client_id: Annotated[UUID, Path(...)],
#     user: UserUpdate,
#     user_id: Auth,
#     db: session
# ) -> User:
#     if not await check_access(user_id, db):
#         raise NoAdminAccessException()

#     return await change_user(client_id, user, db)


@router.post('/ban/{client_id}', status_code=204)
async def ban_user_handler(
    client_id: Annotated[UUID, Path(...)], 
    user_id: Auth, 
    db: session
):
    if not await check_access(user_id, db):
        raise NoAdminAccessException()
    
    await ban_user(client_id, db)


@router.post("/increase_verification/{user_id}")
async def increase_verification_handler(client_id: Auth, db: session, user_id: UUID = Path(...)):
    if not await check_access(client_id, db):
        raise NoAdminAccessException()
    return await increase_verification(user_id, db)