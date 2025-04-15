from datetime import datetime
from pydantic import Field, field_validator
from uuid import UUID

from models.booking import SeatBooking
from .model import OrmModel
from .seats import SeatCoords
from .users import User


class QRData(OrmModel):
    """Data that should be contained in QR"""

    qr_data: str = Field(
        ..., 
        description='''
        json который зашит в QR. Пример: 
        {
            "booking_id": UUID,
            "seat_uuid": UUID
        }
        '''
    )

    # @field_validator('qr_data')
    # def check_valid_data(cls, v):
        
    #     return v

class QRPayload(OrmModel):
    """QR code must contain this data"""

    booking_id: UUID
    seat_uuid: UUID

class QRResponse(OrmModel):
    """When qr is scanned, this model is a response for post method"""

    accept: bool = Field(..., description='Пропускать ли посителя')
    booking_id: UUID
    start_date: datetime
    end_date: datetime

    seat: SeatCoords
    user: User

    need_verification: bool
