from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.auth.repository import UserRepository
from bestiaux.auth.schemas import LoginRequest, RegisterRequest, UserResponse
from bestiaux.auth.service import AuthService
from bestiaux.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(user_repo=UserRepository(session=db))


def _to_response(user: UserEntity) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        currency=user.currency,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    service: AuthService = Depends(_get_auth_service),
) -> UserResponse:
    user = await service.register(body.username, body.email, body.password)
    request.session["user_id"] = str(user.id)
    return _to_response(user)


@router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest,
    request: Request,
    service: AuthService = Depends(_get_auth_service),
) -> UserResponse:
    user = await service.login(body.email, body.password)
    request.session["user_id"] = str(user.id)
    return _to_response(user)


@router.post("/logout")
async def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(user: UserEntity = Depends(get_current_user)) -> UserResponse:
    return _to_response(user)
