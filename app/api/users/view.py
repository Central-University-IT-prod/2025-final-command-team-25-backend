from fastapi import APIRouter, Request, HTTPException

from dependencies import session, Auth
from schemas import (
    User,
    UserCreation,
    AuthRequest,
    Tokens,
    RefreshToken,
    PassportData, UserProfile
)
from .auth import auth_user, refresh_token, logout
from .crud import create_user, get_user, add_passport

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=User
)
async def user_register_handler(creation_data: UserCreation, db: session) -> User:
    return await create_user(creation_data, db)


@router.post("/auth")
async def user_auth_handler(auth_data: AuthRequest, db: session) -> Tokens:
    return await auth_user(auth_data, db)


@router.post("/auth/refresh")
async def user_refresh_handler(
    refresh_request: RefreshToken, db: session
) -> Tokens:
    return await refresh_token(refresh_request, db)


@router.get(
    "/me",
    response_model=UserProfile
)
async def user_me_handler(client_id: Auth, db: session) -> UserProfile:
    return await get_user(client_id, db)


@router.delete(
    "/session",
    status_code=204
)
async def logout_handler(request: Request, db: session) -> None:
    if request.headers.get("Authorization") is None:
        raise HTTPException(status_code=401, detail="missed token")
    token = request.headers.get("Authorization")
    await logout(token, db)


# @router.patch(
#     "/edit",
#     response_model=User
# )
# async def user_update_handler(
#     client_id: Auth, 
#     user_update: UserUpdate, 
#     db: session
# ) -> User:
#     return await change_user(client_id, user_update, db)


@router.post("/add_passport")
async def add_passport_handler(client_id: Auth, passport_data: PassportData, db: session):
    return await add_passport(client_id, passport_data, db)