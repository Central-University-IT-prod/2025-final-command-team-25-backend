from datetime import datetime

from models.base import Base
from sqlalchemy import DateTime, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid


class AuthSessions(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    token_uid: Mapped[str] = mapped_column(nullable=False)
    expire_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
