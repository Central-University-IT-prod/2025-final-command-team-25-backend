from uuid import UUID

from .enums import SeatAccessLevel, RequiredLevel, SeatType
from .model import OrmModel

class SeatCoords(OrmModel):
    seat_uuid: UUID
    seat_id: str
    seat_access_level: SeatAccessLevel
    seat_type: SeatType

    pos_x: float
    pos_y: float
    width: float
    height: float
    rx: float
    rotation: float
    price: float


class SeatFree(SeatCoords, OrmModel):
    is_free: bool
    required_level: RequiredLevel


class TableOut(OrmModel):
    pos_x: float
    pos_y: float
    width: float
    height: float
    rx: float
    rotation: float
