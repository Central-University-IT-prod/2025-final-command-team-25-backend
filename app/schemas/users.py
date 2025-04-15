from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from .model import OrmModel
from .enums import UserAccessLevel, SeatAccessLevel
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=256, description="Имя пользователя")


class UserCreation(UserBase):
    password: str = Field(min_length=8, max_length=256, description="Пароль")


class User(UserBase, OrmModel):
    client_id: UUID = Field(..., description="ID пользователя")
    access_level: UserAccessLevel = Field(..., description="Уровень доступа")


class UserProfile(User):
    verification_level: SeatAccessLevel = Field(..., description="Уровень верификации")


# class UserUpdate(BaseModel):
#     username: Optional[str] = Field(min_length=3, max_length=256, description="Имя пользователя", default=None)
#     access_level: Optional[UserAccessLevel] = Field(description="Уровень доступа", default=None)
#     verification_level: Optional[SeatAccessLevel] = Field(description="Уровень верификации", default=None)


class PassportData(BaseModel):
    series: str = Field(..., description="Серия паспорта")
    number: str = Field(..., description="Номер паспорта")
    name: str = Field(..., description="ФИЩ")