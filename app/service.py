import jwt
from fastapi import HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from db import async_session
from models import UserModel
from sqlalchemy import select
from uuid import UUID

from config import config


class CheckAPIAccess(APIKeyHeader):
    async def __call__(self, request: Request):
        token = await super().__call__(request)
        if token is None:
            raise HTTPException(status_code=401, detail="missed token")
        token = token.replace('Bearer ', '')
        try:
            token_payload = jwt.decode(token, config.TOKEN_SECRET_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        client_id = token_payload["client_id"]

        async with async_session() as session:
            query = select(UserModel).where(UserModel.client_id == client_id)
            result = await session.execute(query)
            result = result.scalar()
            if result is None:
                raise HTTPException(status_code=401, detail="Invalid token no such user")

            if result.is_banned:
                raise HTTPException(status_code=403, detail="User is blocked")

        return client_id


authorize = CheckAPIAccess(auto_error=False, name='Authorization')
