from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, DBSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdateRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(payload: SignupRequest, db: DBSession) -> UserResponse:
    repo = UserRepository(db)

    if await repo.get_by_email(payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if await repo.get_by_username(payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username taken")

    user = await repo.create(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    repo = UserRepository(db)
    user = await repo.get_by_email(payload.email)

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account deactivated")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> UserResponse:
    repo = UserRepository(db)
    updates: dict = {}

    if payload.full_name is not None:
        updates["full_name"] = payload.full_name
    if payload.bio is not None:
        updates["bio"] = payload.bio
    if payload.password:
        updates["hashed_password"] = hash_password(payload.password)

    user = await repo.update(current_user, **updates)
    return UserResponse.model_validate(user)


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(current_user: CurrentUser) -> None:
    # JWT is stateless; client should discard the token.
    # For token revocation, add a Redis blocklist here.
    return None
