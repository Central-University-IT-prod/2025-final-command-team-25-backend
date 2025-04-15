from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID

from .model import OrmModel
from .enums import TimeSlotType
from .users import User

# date_examples = ConfigDict(
#         json_schema_extra={
#             "examples": [
#                 {
#                     'start_date': '2026-01-01T00:00:00',
#                     'end_date': '2026-01-01T01:00:00',
#                 }
#             ]
#         }
#     )


class FreeSeatsFilter(BaseModel):
    start_date: datetime = Field(..., description="Дата начала бронирования")
    end_date: datetime = Field(..., description="Дата конца бронирования")
    tags: Optional[list[str]] = Field(default=[], description="Теги", example=["tag1", "tag2"])

    # model_config = date_examples

    @field_validator("start_date", "end_date")
    def check_alignment(cls, v):
        """
        Проверяем, что минуты кратны 30, а секунды и микросекунды равны нулю
        """
        if v.minute % 30 != 0 or v.second != 0 or v.microsecond != 0:
            raise ValueError("Время должно быть кратно 30 минутам (например, 10:00, 10:30, 11:00...)")
        return v


class SingleSeatBook(OrmModel):
    """Single seat model"""

    seat_id: str = Field(..., description='номер места')
    seat_uuid: UUID = Field(..., description='UUID места')
    # user_id: Optional[UUID] = Field(None, description='id владельца стула')
    
    is_owner: Optional[bool] = Field(False, description='владеет ли этот пользователь бронью на это место')


class BookingObject(OrmModel):
    """User bookings represent"""

    booking_id: UUID
    user_id: UUID
    start_date: datetime
    end_date: datetime
    seats: list[SingleSeatBook]

    invite_url: Optional[str] = Field(None, description='ссылка приглашение')

    # model_config = date_examples

class BookingObjAdmin(BookingObject):
    """Admin can also access user's data"""

    username: str


class RegisterBook(OrmModel):
    start_date: datetime = Field(..., description="Дата начала бронирования")
    end_date: datetime = Field(..., description="Дата конца бронирования")

    seats: list[SingleSeatBook]

    # model_config = date_examples

    @field_validator("start_date", "end_date")
    def check_alignment(cls, v):
        """
        Проверяем, что минуты кратны 30, а секунды и микросекунды равны нулю
        """
        if v.minute % 30 != 0 or v.second != 0 or v.microsecond != 0:
            raise ValueError("Время должно быть кратно 30 минутам (например, 10:00, 10:30, 11:00...)")

        return v


class BookingChange(OrmModel):
    start_date: datetime = Field(..., description="Дата начала бронирования")
    end_date: datetime = Field(..., description="Дата конца бронирования")

    # model_config = date_examples

    @field_validator("start_date", "end_date")
    def check_alignment(cls, v):
        """
        Проверяем, что минуты кратны 30, а секунды и микросекунды равны нулю
        """
        if v.minute % 30 != 0 or v.second != 0 or v.microsecond != 0:
            raise ValueError("Время должно быть кратно 30 минутам (например, 10:00, 10:30, 11:00...)")

        return v


class TimeSlot(OrmModel):
    """Time slot step 30 minute implementation"""

    time: datetime
    slot_type: TimeSlotType


class Invitation(OrmModel):
    
    booking_id: UUID


class InvitationInfo(OrmModel):

    booker: User = Field(..., description='Изначальный пользователь, который делал бронирование')
    seat: SingleSeatBook = Field(..., description='Место, которое назначелось пользователю')

