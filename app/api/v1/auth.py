from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.services.user_service import UserService

from starlette.requests import Request
router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    # 1. Проверяем бизнес-логику (существование)
    if await service.get_by_email(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists.",
        )

    # 2. Делегируем создание сервису
    return await service.create_user(user_in)


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/login/{provider}")
async def social_login(
        provider: str,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Редирект на VK/Yandex.
    """
    service = AuthService(db)
    return await service.get_login_redirect(provider, request, "")


@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(
        provider: str,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Обработка ответа от соцсети.
    """
    service = AuthService(db)
    return await service.authenticate_social_user(provider, request)