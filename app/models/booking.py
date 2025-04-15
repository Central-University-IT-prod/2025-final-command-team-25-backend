import uuid

from sqlalchemy import ForeignKey, TIMESTAMP, UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from models.base import Base
from models.objects import Seats


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.client_id"))
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="bookings")  # type: ignore
    seats: Mapped[list["SeatBooking"]] = relationship(
        "SeatBooking",
        back_populates="booking",
        cascade="all, delete, delete-orphan"
    )

class SeatBooking(Base):
    __tablename__ = "seat_bookings"

    seat_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seats.seat_uuid"), primary_key=True
    )
    seat_id: Mapped[str] = mapped_column(String, nullable=False)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.booking_id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.client_id"), nullable=True)

    seat: Mapped["Seats"] = relationship("Seats") # type: ignore
    booking: Mapped["Booking"] = relationship("Booking", back_populates="seats")
