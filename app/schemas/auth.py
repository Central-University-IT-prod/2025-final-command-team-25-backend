from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    email: str = Field(..., description='Логин', min_length=3, max_length=256)
    password: str = Field(..., description='Пароль', min_length=8, max_length=256)


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(BaseModel):
    access_token: str = Field(..., description='Токен доступа')
    expires_in: int = Field(..., description='Время жизни токена доступа')
    refresh_token: str = Field(..., description='Токен обновления')
    refresh_expires_in: int = Field(..., description='Время жизни токена обновления')
