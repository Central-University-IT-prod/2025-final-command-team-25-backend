# from uuid import uuid4, UUID
import uuid

from sqlalchemy import UUID, Enum, Float, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from schemas import SeatAccessLevel, SeatType


class Seats(Base):
    __tablename__ = "seats"

    seat_id: Mapped[str] = mapped_column(String, nullable=False)
    seat_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coworking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coworkings.coworking_id", ondelete="CASCADE")
    )
    seat_access_level: Mapped[SeatAccessLevel] = mapped_column(
        Enum(SeatAccessLevel, name="accesslevel"), nullable=False, default=SeatAccessLevel.GUEST
    )
    seat_type: Mapped[SeatType] = mapped_column(Enum(SeatType), nullable=False)
    pos_x: Mapped[float] = mapped_column(Float, nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    rx: Mapped[float] = mapped_column(Float, nullable=False)
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    price: Mapped[int] = mapped_column(Integer, nullable=False, default=100 * 100)


class Tables(Base):
    __tablename__ = "tables"

    table_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coworking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coworkings.coworking_id", ondelete="CASCADE")
    )
    pos_x: Mapped[float] = mapped_column(Float, nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    rx: Mapped[float] = mapped_column(Float, nullable=False)
    rotation: Mapped[float] = mapped_column(Float, nullable=False)
