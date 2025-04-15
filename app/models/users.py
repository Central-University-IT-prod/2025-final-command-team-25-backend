import uuid

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship, mapped_column

from models.base import Base
from schemas import UserAccessLevel, SeatAccessLevel, VerificationLevel


class User(Base):
    __tablename__ = "users"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    access_level: Mapped[UserAccessLevel] = mapped_column(
        Enum(UserAccessLevel),
        nullable=False,
        default=UserAccessLevel.GUEST
    )
    verification_level: Mapped[SeatAccessLevel] = mapped_column(
        Enum(VerificationLevel),
        nullable=False,
        default=VerificationLevel.GUEST
    )
    is_banned: Mapped[bool] = mapped_column(nullable=False, default=False)
    passport_series: Mapped[str] = mapped_column(nullable=True)
    passport_number: Mapped[str] = mapped_column(nullable=True)
    passport_name: Mapped[str] = mapped_column(nullable=True)

    bookings: Mapped[list["Booking"]] = relationship( # type: ignore
        back_populates="user", 
        cascade="all, delete, delete-orphan"
    )  
    # admin: Mapped["Admin"] = relationship(back_populates="user", uselist=False)


# class Admin(Base):
#     __tablename__ = "admins"

#     admin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.client_id'), primary_key=True)
#     coworking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('coworkings.coworking_id'))

#     # Связь с пользователем (один к одному)
#     user: Mapped["User"] = relationship("User", back_populates="admin")
#     # Связь с коворкингом (многие администраторы могут принадлежать одному коворкингу)
#     coworking: Mapped["Coworkings"] = relationship("Coworkings", back_populates="admins") # type: ignore
