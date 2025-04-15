from fastapi import APIRouter, Path, UploadFile, File, Form
from .crud import get_seats, get_all_coworkings, get_tables, register_coworking

# from models.objects import Seats
from schemas import CoworkingModel, SeatCoords, CoworkingCreation, SeatFree, TableOut
from dependencies import session
from uuid import UUID
from typing import Annotated
from api.admins.admin_access import check_access
from api.admins.exceptions import NoAdminAccessException
from dependencies import session, Auth

router = APIRouter(prefix="/coworkings", tags=["coworkings"])


@router.get(
    "",
    response_model=list[CoworkingModel]
)
async def get_coworkings(
    db: session
):
    coworkings = await get_all_coworkings(db)
    return coworkings


@router.get(
    "/{coworking_id}/tables", 
    response_model=list[TableOut]
)
async def get_table_pos(
    coworking_id: Annotated[UUID, Path(..., description='id коворкинга')], 
    db: session
):
    seats = await get_tables(coworking_id, db)
    return seats


@router.get(
    "/{coworking_id}/seats", 
    response_model=list[SeatCoords]
)
async def get_seats_pos(
    coworking_id: Annotated[UUID, Path(..., description='id коворкинга')], 
    db: session
) -> list[SeatCoords]:
    seats = await get_seats(coworking_id, db)
    return seats
    
    
@router.post(
    "/create",
    response_model=CoworkingModel
)
async def create_coworking(
    db: session,
    user_id: Auth,
    title: str = Form(..., description='Название коворкинга'),
    address: str = Form(..., description='Адрес коворкинга'),
    tz_offset: int = Form(0, description='Смещение часового пояса коворгина относительно UTC+0 (по умолчанию 0)'),
    file: UploadFile = File(...)
):
    if not await check_access(user_id, db):
        raise NoAdminAccessException()
    
    coworking = await register_coworking(file, title, address, tz_offset, db)
    return coworking
    

