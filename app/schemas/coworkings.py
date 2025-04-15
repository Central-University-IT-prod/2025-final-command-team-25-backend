from pydantic import BaseModel
from uuid import UUID
from fastapi import Form

class CoworkingModel(BaseModel):
    "Coworking representation schema"

    coworking_id: UUID
    title: str
    address: str
    tz_offset: int
    timezone_str: str

class CoworkingCreation(BaseModel):
    "Coworking creation model"

    title: str = Form(..., description='Название коворкинга')
    address: str = Form(..., description='Адрес коворкинга')
    tz_offset: int = Form(0, description='Смещение часового пояса коворгина относительно UTC+0 (по умолчанию 0)')
