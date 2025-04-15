import uuid

from sqlalchemy import String, UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Coworkings(Base):
    __tablename__ = "coworkings"

    coworking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    tz_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # # Один к многим: одно коворкинг может иметь несколько администраторов
    # admins: Mapped[list["Admin"]] = relationship("Admin", back_populates="coworking") # type: ignore

    @property
    def timezone_str(self) -> str:
        """
        Преобразует числовое смещение в строку вида "UTC+X" или "UTC-X".
        """
        sign = '+' if self.tz_offset >= 0 else ''
        return f"UTC{sign}{self.tz_offset}"
    