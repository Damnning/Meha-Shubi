from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import create_access_token
from app.services.user_service import UserService  # <-- Подключаем сервис

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

    # 1. Вся грязная работа с хешами внутри сервиса
    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Роутер отвечает только за выдачу токена (это слой HTTP/Security)
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }