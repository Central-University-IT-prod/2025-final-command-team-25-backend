import datetime
import random
import string
import time

from sqlalchemy import select, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.exceptions import InvalidCredentialsException
from config import config
from schemas import AuthRequest, Tokens, RefreshToken
from models import UserModel, AuthSessionsModel

from bcrypt import checkpw
import jwt


def generate_token_uid() -> str:
    return "".join(random.choices(string.ascii_letters, k=32))


async def auth_user(
        request_data: AuthRequest,
        db: AsyncSession,
) -> Tokens:
    query = select(UserModel).where(UserModel.email == request_data.email)
    user = (await db.execute(query)).scalar()
    if user is None:
        raise InvalidCredentialsException()

    if not checkpw(
            request_data.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise InvalidCredentialsException()

    token_id = generate_token_uid()
    auth_session = AuthSessionsModel(
        client_id=user.client_id,
        token_uid=token_id,
        expire_at=datetime.datetime.now()
                  + datetime.timedelta(seconds=config.REFRESH_TOKEN_EXPIRE_IN),
    )
    db.add(auth_session)
    await db.commit()

    return Tokens(
        access_token=jwt.encode(
            payload={
                "client_id": str(user.client_id),
                "exp": config.ACCESS_TOKEN_EXPIRE_IN + time.time(),
            },
            key=config.TOKEN_SECRET_KEY,
            algorithm="HS256",
        ),
        expires_in=config.ACCESS_TOKEN_EXPIRE_IN,
        refresh_token=jwt.encode(
            payload={
                "client_id": str(user.client_id),
                "token_id": token_id,
                "exp": config.REFRESH_TOKEN_EXPIRE_IN + time.time(),
            },
            key=config.TOKEN_SECRET_KEY,
            algorithm="HS256",
        ),
        refresh_expires_in=config.REFRESH_TOKEN_EXPIRE_IN,
    )


async def refresh_token(request_data: RefreshToken, db: AsyncSession) -> Tokens:
    try:
        token_payload = jwt.decode(
            request_data.refresh_token, config.TOKEN_SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        raise InvalidCredentialsException()

    query = select(AuthSessionsModel).where(
        AuthSessionsModel.token_uid == token_payload["token_id"]
    )
    auth_session = (await db.execute(query)).scalar()
    if auth_session is None:
        raise InvalidCredentialsException()

    query = delete(AuthSessionsModel).where(
        AuthSessionsModel.token_uid == token_payload["token_id"]
    )
    await db.execute(query)

    auth_session = AuthSessionsModel(
        client_id=auth_session.client_id,
        token_uid=generate_token_uid(),
        expire_at=datetime.datetime.now()
                  + datetime.timedelta(seconds=config.REFRESH_TOKEN_EXPIRE_IN),
    )
    db.add(auth_session)
    await db.commit()

    return Tokens(
        access_token=jwt.encode(
            payload={
                "client_id": str(auth_session.client_id),
                "exp": config.ACCESS_TOKEN_EXPIRE_IN + time.time(),
            },
            key=config.TOKEN_SECRET_KEY,
            algorithm="HS256",
        ),
        expires_in=config.ACCESS_TOKEN_EXPIRE_IN,
        refresh_token=jwt.encode(
            payload={
                "client_id": str(auth_session.client_id),
                "token_id": auth_session.token_uid,
                "exp": config.REFRESH_TOKEN_EXPIRE_IN + time.time(),
            },
            key=config.TOKEN_SECRET_KEY,
            algorithm="HS256",
        ),
        refresh_expires_in=config.REFRESH_TOKEN_EXPIRE_IN,
    )


async def logout(token: str, db: AsyncSession) -> None:
    try:
        token_payload = jwt.decode(
            token, config.TOKEN_SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        raise InvalidCredentialsException()

    query = delete(AuthSessionsModel).where(AuthSessionsModel.token_uid == token_payload["token_id"])
    await db.execute(query)
    await db.commit()
