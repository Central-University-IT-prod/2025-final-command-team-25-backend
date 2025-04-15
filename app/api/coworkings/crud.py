import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from pathlib import Path
from uuid import UUID
from models import SeatsModel, CoworkingModel
from models.objects import Tables
from schemas import SeatAccessLevel, SeatType, CoworkingCreation
from tools.extractor import parse_svg
from .exceptions import WrongFileTypeException


async def get_tables(coworking_id: UUID, db: AsyncSession):
    tables = await db.scalars(
        select(Tables)
        .where(Tables.coworking_id == coworking_id)
    )

    return tables.all()


async def get_seats(coworking_id: UUID, db: AsyncSession) -> list[SeatsModel]:
    seats = await db.scalars(
        select(SeatsModel)
        .where(SeatsModel.coworking_id == coworking_id)
    )

    return seats.all()


async def get_all_coworkings(db: AsyncSession) -> list[CoworkingModel]:
    coworkings = await db.scalars(select(CoworkingModel))
    return coworkings.all()


async def register_coworking(
    file: UploadFile,
    title,
    address,
    tz_offset,
    db: AsyncSession
):
    """
    Регистрирует данные коворкинга, полученные из SVG-файла, и сохраняет их в базу.
    Выполняется bulk insert для столов и сидений.
    """
    if file.content_type != "image/svg+xml":
        raise WrongFileTypeException()
    
    try:
        content = await file.read()
        objects = parse_svg(content)
    except:
        raise WrongFileTypeException()

    coworking_id = uuid.uuid4()

    new_coworking = CoworkingModel(
        coworking_id=coworking_id,
        title=title,
        address=address,
        tz_offset=tz_offset
    )
    db.add(new_coworking)
    await db.commit()
    
    # Создаем список объектов для bulk вставки столов
    tables_data = []
    for table in objects['tables']:
        new_table = Tables(
            pos_x=table['x'],
            pos_y=table['y'],
            width=table['width'],
            height=table['height'],
            rx=table['rx'],
            coworking_id=coworking_id,
            rotation=table['rotation']
        )
        tables_data.append(new_table)
    
    # Создаем список объектов для bulk вставки сидений
    seats_data = []
    for seat in objects['seats']:
        new_seat = SeatsModel(
            seat_id=seat['seat_id'],
            coworking_id=coworking_id,
            pos_x=seat['x'],
            pos_y=seat['y'],
            width=seat['width'],
            height=seat['height'],
            rx=seat['rx'],
            rotation=seat['rotation'],
            seat_access_level=SeatAccessLevel(seat['seat_access_level']),
            seat_type=SeatType(seat['seat_type'])
            # price оставляем по умолчанию или можно задать явно
        )
        seats_data.append(new_seat)
    
    # Bulk вставка объектов в базу
    db.add_all(tables_data)
    db.add_all(seats_data)
    await db.commit()

    return new_coworking

